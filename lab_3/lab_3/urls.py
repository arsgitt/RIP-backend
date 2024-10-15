from django.contrib import admin
from team import views
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),

    # Услуги
    path(r'players/', views.PlayerList.as_view(), name='players-list'),  # список игроков (GET),

    path(r'players/<int:pk>/', views.PlayerDetail.as_view(), name='player-detail'),  # получить игрока (GET),
    path(r'players/create/', views.PlayerDetail.as_view(), name='player-create'),
    # добавление игрока (POST),
    path(r'players/update/<int:pk>/', views.PlayerDetail.as_view(), name='player-update'),
    # изменение полей игрока (DELETE),
    path(r'players/delete/<int:pk>/', views.PlayerDetail.as_view(), name='player-delete'),
    # удаление игрока (DELETE),

    path(r'players/add/', views.AddPlayerView.as_view(), name='add-player-to-team'),
    # добавление игрока в заявку (POST),

    path(r'players/image/', views.ImageView.as_view(), name='add-image'),  # замена изображения

    # Заявки
    path(r'list-teams/', views.ListTeams.as_view(), name='list-teams-by-username'),  # получить заявки (GET),
    path(r'team/<int:pk>/', views.GetTeam.as_view(), name='get-team-by-id'),  # получить конкретную заявку (GET),
    path(r'team/<int:pk>/', views.GetTeam.as_view(), name='put-team-by-id'),  # изменить конкретную заявку (PUT),

    path(r'form-team/<int:pk>/', views.FormTeam.as_view(), name='form-team-by-id'),  # формирование заявки (PUT)
    path(r'moderate-team/<int:pk>/', views.ModerateTeam.as_view(), name='moderate-team-by-id'),
    # завершить/отклонить модератором (PUT)
    path(r'delete-team/<int:pk>/', views.ModerateTeam.as_view(), name='delete-team-by-id'),
    # удалить заявку (DELETE)

    # m-m
    path(r'delete-from-team/<int:pk>/', views.EditTeamPlayer.as_view(), name='delete-from-team-by-id'),
    # удалить из заявки (DELETE)
    path(r'add-is_captain/<int:pk>/', views.EditTeamPlayer.as_view(), name='add-is_captain-request-by-id'),

    # Users
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('profile/', views.UserUpdateView.as_view(), name='profile'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
]

