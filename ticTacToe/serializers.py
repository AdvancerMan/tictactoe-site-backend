from rest_framework import serializers

from .models import Game


class GameListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'width', 'height', 'win_threshold',
                  'owner', 'creation_time')


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        exclude = ("field",)
