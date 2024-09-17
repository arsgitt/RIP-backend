from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home_url'),
    path('player/<int:id>/', views.player, name='player_url'),
    path('basket/', views.basket, name='basket_url'),
    path('search/', views.search, name='search_url'),
]
