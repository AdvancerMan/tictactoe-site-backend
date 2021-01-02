from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models

game_size_validator = MaxValueValidator(100)


def get_admin():
    return User.objects.get(username='admin').id


class Game(models.Model):
    width = models.PositiveIntegerField(validators=[game_size_validator])
    height = models.PositiveIntegerField(validators=[game_size_validator])
    win_threshold = models.PositiveIntegerField(
        validators=[game_size_validator]
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=get_admin)
    players = models.ManyToManyField(User, related_name='tic_tac_toe_games')
    # if not started:
    #     object[int:id -> str:hex_code]
    # else:
    #     list[str:hex_code] (according to order)
    colors = models.JSONField()
    # list[int:id]
    order = models.JSONField(default=list, blank=True)
    # list[tuple[int:i, int:j]]
    history = models.JSONField(default=list, blank=True)

    # field and history must not have conflicts
    # if null so history should be used
    # (field can be initialized from history at any time)
    # list[list[int:player_index or -1]]
    field = models.JSONField(default=None, null=True, blank=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    started = models.BooleanField(default=False)
    winner_index = models.BooleanField(default=None, null=True)

    def __str__(self):
        return f"[{'started' if self.started else 'waiting'}] " \
               f"{self.width}x{self.height}x{self.win_threshold} game with " \
               f"[{', '.join(str(u) for u in self.players.all())}]"
