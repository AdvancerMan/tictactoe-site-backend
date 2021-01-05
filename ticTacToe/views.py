from abc import abstractmethod, ABC
import random

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .forms import PageCountForm, GameForm, JoinForm, TurnForm, \
    HistorySuffixForm, MyGamesForm
from .models import Game
from .serializers import (
    GameSerializer, GameListSerializer,
    WinDataSerializer, GameColorsSerializer,
    GamePlayersSerializer
)


class MyListView(APIView, ABC):
    @abstractmethod
    def get_query_set(self):
        return None

    @abstractmethod
    def get_serializer_class(self):
        return None

    def get(self, request):
        form = PageCountForm(request.GET)
        if not form.is_valid():
            return Response({'errors': form.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        data = form.cleaned_data
        page = data['page']
        count = data['count']

        objects = self.get_query_set()[(page - 1) * count:page * count]
        serializer = self.get_serializer_class()(objects, many=True)
        return Response(serializer.data)


class StartedGamesView(MyListView):
    permission_classes = []

    def get_query_set(self):
        return Game.objects.filter(started=True)

    def get_serializer_class(self):
        return GameListSerializer


class GameDetailView(APIView):
    permission_classes = []

    def head(self, request, pk):
        game = Game.objects.filter(id=pk)
        if not game:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response()

    def get(self, request, pk):
        game = Game.objects.filter(id=pk)
        if not game:
            return Response({'errors': {'pk': 'Game pk is invalid'}},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = GameSerializer(game.first())
        return Response(serializer.data)


class WaitingGamesView(MyListView):
    permission_classes = []

    def get_query_set(self):
        return Game.objects.filter(started=False)

    def get_serializer_class(self):
        return GameListSerializer


class CreateGameView(APIView):
    def post(self, request):
        if request.user.tic_tac_toe_games.filter(started=False):
            return Response({'errors': {
                'user': 'You can not create a game while you are in other game'
            }}, status=status.HTTP_400_BAD_REQUEST)

        form = GameForm(request.data)
        if not form.is_valid():
            return Response({'errors': form.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        # it is not a copy of form.cleaned_data
        data = form.cleaned_data
        data['colors'] = {
            request.user.id: data['owner_color']
        }
        del data['owner_color']
        data['owner'] = request.user

        game = Game.objects.create(**data)
        game.players.add(request.user)
        return Response({"id": game.id})


class JoinGameView(APIView):
    def patch(self, request, pk):
        if request.user.tic_tac_toe_games.filter(started=False):
            return Response({'errors': {
                'user': 'You can not join a game while you are in other game'
            }}, status=status.HTTP_400_BAD_REQUEST)

        game = Game.objects.filter(id=pk).first()
        if not game:
            return Response({'errors': {'pk': 'Game pk is invalid'}},
                            status=status.HTTP_400_BAD_REQUEST)

        if game.started:
            return Response({'errors': {
                'game': 'This game has already started'
            }}, status=status.HTTP_400_BAD_REQUEST)

        # TODO validate number of players < available and lock a mutex

        form = JoinForm(request.data)
        if not form.is_valid():
            return Response({'errors': form.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        data = form.cleaned_data

        if data['color'] in game.colors.values():
            return Response({'errors': {'color': 'Color is already in use'}},
                            status=status.HTTP_400_BAD_REQUEST)

        game.players.add(request.user)
        game.colors[request.user.id] = data['color']
        game.save()
        return Response()


class StartGameView(APIView):
    def patch(self, request, pk):
        game = Game.objects.filter(id=pk).first()
        if not game:
            return Response({'errors': {'pk': 'Game pk is invalid'}},
                            status=status.HTTP_400_BAD_REQUEST)

        if game.owner_id != request.user.id:
            return Response({'errors': {'user': 'You are not the owner'}},
                            status=status.HTTP_403_FORBIDDEN)

        if game.started:
            return Response({'errors': {'game': 'Game has already started'}},
                            status=status.HTTP_400_BAD_REQUEST)

        game.order = list([player.id for player in game.players.all()])
        random.shuffle(game.order)
        game.colors = [game.colors[str(player_id)] for player_id in game.order]
        game.started = True
        game.save()

        return Response()


class MakeTurnView(APIView):
    def check_captured(self, i, j, game, captured):
        for step_i in range(-1, 2):
            for step_j in range(-1, 2):
                if (captured[step_i + 1][step_j + 1]
                        + captured[-step_i + 1][-step_j + 1] + 1
                        >= game.win_threshold):
                    start_i = i + step_i * captured[step_i + 1][step_j + 1]
                    start_j = j + step_j * captured[step_i + 1][step_j + 1]
                    return {
                        'start_i': start_i,
                        'start_j': start_j,
                        'direction_i': -step_i,
                        'direction_j': -step_j,
                    }

    def check_win_field(self, i, j, game):
        captured = [[0] * 3 for _ in range(3)]
        for step_i in range(-1, 2):
            for step_j in range(-1, 2):
                if step_i == 0 and step_j == 0:
                    continue
                for distance in range(1, game.win_threshold):
                    check_i = i + step_i * distance
                    check_j = j + step_j * distance
                    if (check_i < 0 or check_i >= game.height
                            or check_j < 0 or check_j >= game.width):
                        break
                    if game.field[check_i][check_j] == game.field[i][j]:
                        captured[step_i + 1][step_j + 1] = distance
                    else:
                        break

        return self.check_captured(i, j, game, captured)

    def check_win_history(self, i, j, game):
        history_sorted = sorted(
            game.history[(len(game.history) - 1) % len(game.order)
                         ::len(game.order)],
            key=lambda p: abs(p[0] - i) + abs(p[1] - j)
        )
        captured = [[0] * 3 for _ in range(3)]

        for turn in history_sorted:
            delta_i = turn[0] - i
            delta_j = turn[1] - j
            max_abs = max(abs(delta_i), abs(delta_j))
            if (abs(delta_i) == abs(delta_j) or 0 in (delta_j, delta_i)) \
                    and max_abs != 0:
                step_i = delta_i // max_abs
                step_j = delta_j // max_abs
                if captured[step_i + 1][step_j + 1] + 1 == max_abs:
                    captured[step_i + 1][step_j + 1] = max_abs

        return self.check_captured(i, j, game, captured)

    def init_field(self, game):
        game.field = [[-1] * game.width for _ in range(game.height)]
        for i in range(len(game.history)):
            turn = game.history[i]
            game.field[turn[0]][turn[1]] = i % len(game.order)

    def check_win(self, i, j, game):
        if game.field is None \
                and len(game.history) > 2 * min(game.width, game.height):
            self.init_field(game)

        if game.field is not None:
            return self.check_win_field(i, j, game)
        else:
            return self.check_win_history(i, j, game)

    def patch(self, request, pk):
        game = Game.objects.filter(id=pk).first()
        # TODO move all validation to form
        if not game:
            return Response({'errors': {'pk': 'Game pk is invalid'}},
                            status=status.HTTP_400_BAD_REQUEST)

        if game.finished:
            return Response({'errors': {'game': 'Game has already finished'}},
                            status=status.HTTP_400_BAD_REQUEST)

        form = TurnForm(request.data)
        if not form.is_valid():
            return Response({'errors': form.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        turn_user_index = len(game.history) % game.players.count()
        turn_user_id = game.order[turn_user_index]
        if turn_user_id != request.user.id:
            return Response({'errors': {'user': 'It is not your turn'}},
                            status=status.HTTP_403_FORBIDDEN)

        i = form.cleaned_data['i']
        j = form.cleaned_data['j']
        if i < 0 or i >= game.height:
            return Response({'errors': {
                'i': f'Not in range (0, {game.height})'
            }}, status=status.HTTP_400_BAD_REQUEST)

        if j < 0 or j >= game.width:
            return Response({'errors': {
                'j': f'Not in range (0, {game.width})'
            }}, status=status.HTTP_400_BAD_REQUEST)

        if (game.field is not None and game.field[i][j] != -1
                or game.field is None and [i, j] in game.history):
            return Response({'errors': {
                ind: f'Cell ({i}, {j}) is already busy'
                for ind in ('i', 'j')
            }}, status=status.HTTP_400_BAD_REQUEST)

        game.history.append([i, j])
        if game.field:
            game.field[i][j] = turn_user_index
        if win_data := self.check_win(i, j, game):
            game.win_line_start_i = win_data['start_i']
            game.win_line_start_j = win_data['start_j']
            game.win_line_direction_i = win_data['direction_i']
            game.win_line_direction_j = win_data['direction_j']
            game.field = None
        elif len(game.history) == game.width * game.height:
            game.win_line_start_i = -1
            game.win_line_start_j = -1
            game.field = None

        game.save()
        return Response(WinDataSerializer(game).data)


class HistorySuffixView(APIView):
    def get(self, request, pk):
        game = Game.objects.filter(id=pk).first()
        # TODO move all validation to form
        if not game:
            return Response({'errors': {'pk': 'Game pk is invalid'}},
                            status=status.HTTP_400_BAD_REQUEST)

        form = HistorySuffixForm(request.GET)
        if not form.is_valid():
            return Response({'errors': form.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        start_index = form.cleaned_data['start_index']
        response = {'history': game.history[start_index:]}
        if game.win_line_start_i is not None:
            response['win_data'] = WinDataSerializer(game).data
        return Response(response)


class GamePlayersView(APIView):
    def get(self, request, pk):
        game = Game.objects.filter(id=pk).first()
        if not game:
            return Response({'errors': {'pk': 'Game pk is invalid'}},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({
            **GamePlayersSerializer(game.players).data,
            **GameColorsSerializer(game).data
        })


class MyGamesView(APIView):
    def get(self, request):
        form = MyGamesForm(request.GET)
        if not form.is_valid():
            return Response({'errors': form.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        finished = form.cleaned_data.get('finished')
        query_set = request.user.tic_tac_toe_games
        if finished is None:
            games = query_set.all()
        elif finished:
            games = Game.finished_query(query_set)
        else:
            games = Game.unfinished_query(query_set)
        return Response(GameListSerializer(games, many=True).data)
