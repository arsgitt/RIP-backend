from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home_url'),
    path('player/<int:id>/', views.player, name='player_url'),
    path('basket/<int:id>/', views.basket, name='basket_url'),
    path('add-player/', views.add_player, name='add_player'),
    path('del-team/', views.del_team, name='del_team'),
]
