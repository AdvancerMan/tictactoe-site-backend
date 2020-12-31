from django.db import models


class Game(models.Model):
    width = models.IntegerField()
    height = models.IntegerField()
    winThreshold = models.IntegerField()
    players = models.JSONField()  # list[int:user_id]
    colors = models.JSONField()  # list[str:hex_code]
    history = models.JSONField()  # list[tuple[int:i, int:j, int:user_index]]
    creationTime = models.DateTimeField(auto_now=True)
