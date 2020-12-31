from rest_framework import serializers

from .models import Game


class GameListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('width', 'height', 'winThreshold', 'players', 'creationTime')


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('width', 'height', 'winThreshold', 'players',
                  'colors', 'history', 'creationTime')
