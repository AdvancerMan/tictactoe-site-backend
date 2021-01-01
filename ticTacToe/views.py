from abc import abstractmethod, ABC
from random import shuffle

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .forms import PageCountForm, GameForm, JoinForm, TurnForm
from .models import Game
from .serializers import GameSerializer, GameListSerializer


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
        serializer = GameSerializer(game)
        return Response(serializer.data)


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
        return Response(GameSerializer(game).data)


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
        shuffle(game.order)
        game.started = True
        game.save()

        return Response()


class MakeTurnView(APIView):
    def patch(self, request, pk):
        game = Game.objects.filter(id=pk).first()
        if not game:
            return Response({'errors': {'pk': 'Game pk is invalid'}},
                            status=status.HTTP_400_BAD_REQUEST)

        form = TurnForm(request.data)
        if not form.is_valid():
            return Response({'errors': form.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        turn_user_id = game.order[len(game.history) % game.players.count()]
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

        if [i, j] in game.history:
            return Response({'errors': {
                ind: f'Cell ({i}, {j}) is already busy'
                for ind in ('i', 'j')
            }}, status=status.HTTP_400_BAD_REQUEST)

        # TODO validate field and finish the game if it is needed
        game.history.append((i, j))
        game.save()
        return Response()
