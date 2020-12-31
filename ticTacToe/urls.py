from django.urls import path

from ticTacToe.views import GameDetailView, GameListView

urlpatterns = [
    path('game/<int:pk>/', GameDetailView.as_view(), name='game'),
    path('games', GameListView.as_view(), name='games'),
]
