from django.urls import path

from ticTacToe.views import (
    GameDetailView, StartedGamesView,
    WaitingGamesView, CreateGameView,
    JoinGameView, StartGameView,
    MakeTurnView, HistorySuffixView,
    GamePlayersView
)

urlpatterns = [
    path('game/<int:pk>', GameDetailView.as_view(), name='game'),
    path('game/<int:pk>/players', GamePlayersView.as_view(), name='players'),
    path('game/<int:pk>/join', JoinGameView.as_view(), name='join'),
    path('game/<int:pk>/start', StartGameView.as_view(), name='start'),
    path('game/<int:pk>/turn', MakeTurnView.as_view(), name='start'),
    path('game/<int:pk>/historySuffix', HistorySuffixView.as_view(),
         name='historySuffix'),
    path('games/started', StartedGamesView.as_view(), name='startedGames'),
    path('games/waiting', WaitingGamesView.as_view(), name='waitingGames'),
    path('games/create', CreateGameView.as_view(), name='create'),
]
