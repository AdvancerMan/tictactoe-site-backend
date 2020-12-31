from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import PageCountForm
from .models import Game
from .serializers import GameSerializer, GameListSerializer


class GameListView(APIView):
    def get(self, request):
        form = PageCountForm(request.GET)
        if not form.is_valid():
            return Response({'errors': form.errors})

        data = form.cleaned_data
        page = data['page']
        count = data['count']

        games = Game.objects.all()[(page - 1) * count:page * count]
        serializer = GameListSerializer(games, many=True)
        return Response(serializer.data)


class GameDetailView(APIView):
    def get(self, request, pk):
        game = Game.objects.filter(id=pk)
        if not game:
            return Response({'errors': {'pk': 'Game pk is invalid'}})
        serializer = GameSerializer(game.first())
        return Response(serializer.data)
