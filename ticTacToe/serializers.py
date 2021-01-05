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
    start = serializers.SerializerMethodField('get_win_line_start')
    direction = serializers.SerializerMethodField(
        'get_win_line_direction'
    )

    def get_win_line_start(self, game):
        return game.win_line_start_i, game.win_line_start_j

    def get_win_line_direction(self, game):
        return game.win_line_direction_i, game.win_line_direction_j

    class Meta:
        model = Game
        fields = ['start', 'direction']


class GamePlayersSerializer(serializers.ModelSerializer):
    players = serializers.SerializerMethodField('get_players')

    def get_players(self, game):
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
        fields = ['players']


class GameColorsSerializer(serializers.ModelSerializer):
    colors = serializers.SerializerMethodField('get_colors')

    def get_colors(self, game):
        if not game.started:
            return [color for _, color in sorted(game.colors.items())]
        else:
            return game.colors

    class Meta:
        model = Game
        fields = ['colors']


class GameSerializer(serializers.ModelSerializer):
    players = serializers.SerializerMethodField('get_players')
    colors = serializers.SerializerMethodField('get_colors')
    win_data = serializers.SerializerMethodField('get_win_data')

    def get_players(self, game):
        return GamePlayersSerializer(game).data['players']

    def get_colors(self, game):
        return GameColorsSerializer(game).data['colors']

    def get_win_data(self, game):
        return WinDataSerializer(game).data

    class Meta:
        model = Game
        exclude = ("field", "win_line_start_i", "win_line_start_j",
                   "win_line_direction_i", "win_line_direction_j")
