from django.db import models


class Game(models.Model):
    width = models.IntegerField()
    height = models.IntegerField()
    winThreshold = models.IntegerField()
    # list[int:user_id]
    players = models.JSONField()
    # list[str:hex_code]
    colors = models.JSONField()
    # list[tuple[int:i, int:j, int:user_index]]
    history = models.JSONField(default=list, blank=True)
    creationTime = models.DateTimeField(auto_now=True)
