from django.urls import path

from ticTacToe.views import (
    GameDetailView, StartedGamesView,
    WaitingGamesView, CreateGameView,
    JoinGameView, StartGameView,
    MakeTurnView, HistorySuffixView,
    GamePlayersView, MyGamesView
)

urlpatterns = [
    path('game/<int:pk>', GameDetailView.as_view(), name='game'),
    path('game/<int:pk>/players', GamePlayersView.as_view(), name='players'),
    path('game/<int:pk>/join', JoinGameView.as_view(), name='join'),
    path('game/<int:pk>/start', StartGameView.as_view(), name='start'),
    path('game/<int:pk>/turn', MakeTurnView.as_view(), name='start'),
    path('game/<int:pk>/historySuffix', HistorySuffixView.as_view(),
         name='history_suffix'),
    path('games/my', MyGamesView.as_view(), name='my_games'),
    path('games/started', StartedGamesView.as_view(), name='started_games'),
    path('games/waiting', WaitingGamesView.as_view(), name='waiting_games'),
    path('games/create', CreateGameView.as_view(), name='create'),
]
