from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Game
from . import service


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class GameListSerializer(serializers.ModelSerializer):
    owner = PlayerSerializer()
    winner = PlayerSerializer()

    class Meta:
        model = Game
        fields = ('id', 'width', 'height', 'win_threshold', 'winner',
                  'owner', 'creation_time', 'started', 'finished')


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
    finished = serializers.BooleanField()

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


class CreateGameSerializer(serializers.ModelSerializer):
    owner_color = serializers.RegexField(r'^#[0-9a-fA-F]{6}$')

    def validate(self, data):
        width = data.get('width', 0)
        height = data.get('height', 0)
        win_threshold = data.get('win_threshold', 0)

        if win_threshold > width or win_threshold > height:
            raise ValidationError(
                "Win threshold should not be more than width and height"
            )

        return data

    def create(self, validated_data):
        owner = validated_data['owner']
        colors = {owner.id: validated_data['owner_color']}
        data_copy = {k: v for k, v in validated_data.items()
                     if k != 'owner_color'}
        game = Game.objects.create(**data_copy, colors=colors)
        game.players.add(owner)
        return game

    class Meta:
        model = Game
        fields = ['width', 'height', 'win_threshold', 'owner_color']


class JoinSerializer(serializers.Serializer):
    color = serializers.RegexField(r'^#[0-9a-fA-F]{6}$')

    def validate_color(self, color):
        if color in self.instance.colors.values():
            raise serializers.ValidationError('Color is already in use')
        return color

    def update(self, game, validated_data):
        user = validated_data['user']
        game.players.add(user)
        game.colors[user.id] = validated_data['color']
        game.save()
        return game


class TurnSerializer(serializers.Serializer):
    i = serializers.IntegerField(min_value=0, max_value=99)
    j = serializers.IntegerField(min_value=0, max_value=99)

    def validate_i(self, i):
        if i >= self.instance.height:
            raise serializers.ValidationError(
                f'Should be less than {self.instance.height}'
            )
        return i

    def validate_j(self, j):
        if j >= self.instance.width:
            raise serializers.ValidationError(
                f'Should be less than {self.instance.width}'
            )
        return j

    def validate(self, data):
        i, j = data['i'], data['j']
        game = self.instance
        if (game.field is not None and game.field[i][j] != -1
                or game.field is None and [i, j] in game.history):
            raise serializers.ValidationError(
                f'Cell ({i}, {j}) is already busy'
            )
        return data

    def update(self, game, validated_data):
        i, j = validated_data['i'], validated_data['j']
        game.history.append([i, j])
        if game.field:
            game.field[i][j] = len(game.history) % len(game.order)

        if win_data := service.check_win(i, j, game):
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
        return game
