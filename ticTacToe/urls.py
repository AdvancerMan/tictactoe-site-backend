from django.urls import path

from ticTacToe.views import (
    GameDetailView, StartedGamesView,
    WaitingGamesView
)

urlpatterns = [
    path('game/<int:pk>', GameDetailView.as_view(), name='game'),
    path('games/started', StartedGamesView.as_view(), name='startedGames'),
    path('games/waiting', WaitingGamesView.as_view(), name='waitingGames'),
]
