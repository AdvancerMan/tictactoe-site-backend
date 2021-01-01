from abc import abstractmethod, ABC

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .forms import PageCountForm, GameForm
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
                'user': 'You can not create more than 1 game at the same time'
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
