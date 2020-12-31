from django.core.validators import MaxValueValidator
from django.db import models


game_size_validator = MaxValueValidator(1000)


class Game(models.Model):
    width = models.PositiveIntegerField(validators=[game_size_validator])
    height = models.PositiveIntegerField(validators=[game_size_validator])
    winThreshold = models.PositiveIntegerField(validators=[game_size_validator])
    # list[int:user_id]
    players = models.JSONField(default=list)
    # list[str:hex_code]
    colors = models.JSONField(default=list)
    # list[tuple[int:i, int:j, int:user_index]]
    history = models.JSONField(default=list, blank=True)
    creationTime = models.DateTimeField(auto_now=True)
