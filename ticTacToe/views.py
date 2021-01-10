import re
from abc import abstractmethod, ABC
import random

from django.http import HttpResponse, HttpResponseNotFound
from django.views import View
from rest_framework import serializers, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from . import service
from .forms import PageCountForm, HistorySuffixForm, MyGamesForm
from .models import Game
from .serializers import (
    GameSerializer, GameListSerializer,
    WinDataSerializer, GameColorsSerializer,
    GamePlayersSerializer, CreateGameSerializer, JoinSerializer, TurnSerializer
)


class MyListView(APIView, ABC):
    @abstractmethod
    def get_query_set(self, request):
        return None

    @abstractmethod
    def get_serializer_class(self):
        return None

    def inject_data(self, objects, serialized, request):
        return serialized

    def get(self, request, *args, **kwargs):
        form = PageCountForm(request.GET)
        if not form.is_valid():
            raise serializers.ValidationError(form.errors)

        data = form.cleaned_data
        page = data['page']
        count = data['count']

        objects = self.get_query_set(request, *args, **kwargs)
        page_objects = objects[(page - 1) * count:page * count]
        serializer = self.get_serializer_class()(page_objects, many=True)
        serialized = serializer.data
        serialized = self.inject_data(
            page_objects, serialized, request, *args, **kwargs
        )
        return Response(serialized)


class AbstractGameListView(MyListView, ABC):
    def get_serializer_class(self):
        return GameListSerializer

    def inject_data(self, games, serialized, request, *args, **kwargs):
        for game, serialized_game in zip(games, serialized):
            serialized_game['user_joined'] = request.user in game.players.all()
        return serialized


class StartedGamesView(AbstractGameListView):
    permission_classes = []

    def get_query_set(self, request):
        return Game.objects.filter(started=True).order_by('-creation_time')


class GameDetailView(APIView):
    permission_classes = []

    def validate(self, pk):
        game = Game.objects.filter(id=pk).first()
        if not game:
            raise exceptions.NotFound()
        return game

    def get(self, request, pk):
        game = self.validate(pk)
        serializer = GameSerializer(game)
        return Response(serializer.data)


class WaitingGamesView(AbstractGameListView):
    permission_classes = []

    def get_query_set(self, request):
        return Game.objects.filter(started=False).order_by('-creation_time')


class CreateGameView(APIView):
    def validate(self, request):
        if request.user.tic_tac_toe_games.filter(started=False):
            raise serializers.ValidationError({
                '__all__': 'You can not create a game'
                           ' while you are in other game'
            })

    def post(self, request):
        self.validate(request)
        serializer = CreateGameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        game = serializer.save(owner=request.user)
        return Response({'id': game.id})


class JoinGameView(APIView):
    def validate(self, request, pk):
        if request.user.tic_tac_toe_games.filter(started=False):
            raise serializers.ValidationError({
                '__all__': 'You can not join a game while you are in other game'
            })

        game = Game.objects.filter(id=pk).first()
        if game is None:
            raise exceptions.NotFound()
        if game.started:
            raise serializers.ValidationError({
                'game': 'The game has already started'
            })
        return game

    def patch(self, request, pk):
        game = self.validate(request, pk)
        serializer = JoinSerializer(game, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response()


class StartGameView(APIView):
    def valdidate(self, request, pk):
        game = Game.objects.filter(id=pk).first()
        if game is None:
            raise exceptions.NotFound()

        if game.owner_id != request.user.id:
            raise exceptions.PermissionDenied({'user': 'You are not the owner'})

        if game.started:
            raise serializers.ValidationError({
                'game': 'Game has already started'
            })
        return game

    def patch(self, request, pk):
        game = self.valdidate(request, pk)
        game.order = list([player.id for player in game.players.all()])
        random.shuffle(game.order)
        game.colors = [game.colors[str(player_id)] for player_id in game.order]
        game.started = True
        game.save()

        return Response()


class MakeTurnView(APIView):
    def validate(self, request, pk):
        game = Game.objects.filter(id=pk).first()
        if game is None:
            raise exceptions.NotFound()

        if not game.started:
            raise serializers.ValidationError({
                'game': 'Game has not started yet'
            })

        if game.finished:
            raise serializers.ValidationError({
                'game': 'Game has already finished'
            })

        turn_user_index = len(game.history) % len(game.order)
        turn_user_id = game.order[turn_user_index]
        if turn_user_id != request.user.id:
            raise exceptions.PermissionDenied({
                'user': 'It is not your turn'
            })
        return game

    def patch(self, request, pk):
        game = self.validate(request, pk)
        serializer = TurnSerializer(game, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(WinDataSerializer(game).data)


class HistorySuffixView(APIView):
    permission_classes = []

    def validate(self, pk):
        game = Game.objects.filter(id=pk).first()
        if game is None:
            raise exceptions.NotFound()
        return game

    def get(self, request, pk):
        game = self.validate(pk)

        form = HistorySuffixForm(request.GET)
        if not form.is_valid():
            raise serializers.ValidationError(form.errors)

        start_index = form.cleaned_data['start_index']
        response = {'history': game.history[start_index:]}
        if game.win_line_start_i is not None:
            response['win_data'] = WinDataSerializer(game).data
        return Response(response)


class GamePlayersView(APIView):
    permission_classes = []

    def validate(self, pk):
        game = Game.objects.filter(id=pk).first()
        if game is None:
            raise exceptions.NotFound()
        return game

    def get(self, request, pk):
        game = self.validate(pk)
        return Response({
            **GamePlayersSerializer(game).data,
            **GameColorsSerializer(game).data
        })


class GameStartedView(APIView):
    permission_classes = []

    def validate(self, pk):
        game = Game.objects.filter(id=pk).first()
        if game is None:
            raise exceptions.NotFound()
        return game

    def get(self, request, pk):
        game = self.validate(pk)
        return Response({'started': game.started})


class MyGamesView(AbstractGameListView):
    def get_query_set(self, request):
        form = MyGamesForm(request.GET)
        if not form.is_valid():
            raise serializers.ValidationError(form.errors)

        finished = form.cleaned_data.get('finished')
        query_set = request.user.tic_tac_toe_games
        if finished is None:
            query_set = query_set.all()
        elif finished:
            query_set = Game.finished_query(query_set)
        else:
            query_set = Game.unfinished_query(query_set)
        query_set = query_set.order_by('-creation_time')
        return query_set


class CircleCrossPictureView(View):
    color_regex = re.compile('[0-9a-fA-F]{6}')

    def get(self, request, name, rgb):
        if name != 'cross' and name != 'circle':
            return HttpResponseNotFound()
        if not self.color_regex.match(rgb):
            return HttpResponseNotFound()

        r = int(rgb[:2], 16)
        g = int(rgb[2:4], 16)
        b = int(rgb[4:], 16)
        if r > 255 or g > 255 or b > 255:
            return HttpResponseNotFound()

        result = service.generate_image_bytes(r, g, b, name)
        return HttpResponse(result, content_type='image/png')
