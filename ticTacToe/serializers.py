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


class WinDataSerializer(serializers.ModelSerializer):
    win_line_start = serializers.SerializerMethodField('get_win_line_start')
    win_line_direction = serializers.SerializerMethodField(
        'get_win_line_direction'
    )

    def get_win_line_start(self, game):
        return game.win_line_start_i, game.win_line_start_j

    def get_win_line_direction(self, game):
        return game.win_line_direction_i, game.win_line_direction_j

    class Meta:
        model = Game
        fields = ['win_line_start', 'win_line_direction']


class GameSerializer(serializers.ModelSerializer):
    players = serializers.SerializerMethodField('sorted_players')
    win_data = serializers.SerializerMethodField('get_win_data')

    def sorted_players(self, game):
        serialized_players = PlayerSerializer(game.players, many=True).data
        if not game.started:
            return sorted(serialized_players, key=lambda p: p['id'])
        else:
            player_to_index = {uid: i for uid, i
                               in zip(game.order, range(len(game.order)))}
            return sorted(serialized_players,
                          key=lambda p: player_to_index[p['id']])

    def get_win_data(self, game):
        return WinDataSerializer(game).data

    class Meta:
        model = Game
        exclude = ("field", "win_line_start_i", "win_line_start_j",
                   "win_line_direction_i", "win_line_direction_j")
