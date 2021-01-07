from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

game_size_validators = [MinValueValidator(1), MaxValueValidator(100)]


class Game(models.Model):
    width = models.PositiveIntegerField(validators=game_size_validators)
    height = models.PositiveIntegerField(validators=game_size_validators)
    win_threshold = models.PositiveIntegerField(
        validators=game_size_validators
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    players = models.ManyToManyField(User, related_name='tic_tac_toe_games')
    # if not started:
    #     dict[int:id -> str:hex_code]
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

    win_line_start_i = models.IntegerField(default=None, null=True, blank=True,
                                           validators=game_size_validators)
    win_line_start_j = models.IntegerField(default=None, null=True, blank=True,
                                           validators=game_size_validators)
    win_line_direction_i = models.IntegerField(default=None, null=True,
                                               blank=True)
    win_line_direction_j = models.IntegerField(default=None, null=True,
                                               blank=True)

    @property
    def str_status(self):
        if self.finished:
            return 'finished'
        elif self.started:
            return 'started'
        else:
            return 'waiting'

    def __str__(self):
        return f"[{self.str_status}] " \
               f"{self.width}x{self.height}x{self.win_threshold} game with " \
               f"[{', '.join(str(u) for u in self.players.all())}]"

    @property
    def finished(self):
        return self.win_line_start_i is not None

    @staticmethod
    def finished_query(query_set):
        return query_set.filter(win_line_start_i__isnull=False)

    @staticmethod
    def unfinished_query(query_set):
        return query_set.filter(win_line_start_i__isnull=True)
