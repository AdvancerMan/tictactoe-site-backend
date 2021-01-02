from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Game


class GameListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'width', 'height', 'win_threshold',
                  'owner', 'creation_time')


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class GameSerializer(serializers.ModelSerializer):
    players = serializers.SerializerMethodField('sorted_players')

    def sorted_players(self, game):
        serialized_players = PlayerSerializer(game.players, many=True).data
        if not game.started:
            return sorted(serialized_players, key=lambda p: p['id'])
        else:
            player_to_index = {uid: i for uid, i
                               in zip(game.order, range(len(game.order)))}
            return sorted(serialized_players,
                          key=lambda p: player_to_index[p['id']])

    class Meta:
        model = Game
        exclude = ("field",)
