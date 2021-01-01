from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models

game_size_validator = MaxValueValidator(1000)


class Game(models.Model):
    width = models.PositiveIntegerField(validators=[game_size_validator])
    height = models.PositiveIntegerField(validators=[game_size_validator])
    win_threshold = models.PositiveIntegerField(
        validators=[game_size_validator]
    )
    players = models.ManyToManyField(User, related_name='tic_tac_toe_games')
    # object[int:id -> str:hex_code]
    colors = models.JSONField()
    # list[int:id]
    order = models.JSONField(default=list, blank=True)
    # list[tuple[int:i, int:j]]
    history = models.JSONField(default=list, blank=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    started = models.BooleanField(default=False)

    def __str__(self):
        return f"[{'started' if self.started else 'waiting'}] " \
               f"{self.width}x{self.height}x{self.win_threshold} game with " \
               f"[{', '.join(str(u) for u in self.players.all())}]"
