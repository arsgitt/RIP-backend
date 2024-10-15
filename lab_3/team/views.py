from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .serializers import *
from .models import Team, Player, TeamPlayer
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from datetime import datetime


class PlayerList(APIView):
    model_class = Player
    serializer_class = PlayerListSerializer

    def get(self, request):
        if 'l_name' in request.GET:
            players = self.model_class.objects.filter(l_name__icontains=request.GET['l_name'])
        else:
            players = self.model_class.objects.all()

        serializer = self.serializer_class(players, many=True)
        resp = serializer.data
        draft_request = Team.objects.filter(user=request.user, status='draft').first()
        if draft_request:
            request_serializer = TeamSerializer(draft_request)  # Use RequestSerializer here
            resp.append({'request': request_serializer.data})

        return Response(resp, status=status.HTTP_200_OK)


class PlayerDetail(APIView):
    model_class = Player
    serializer_class = PlayerDetailSerializer

    # получить игрока
    def get(self, request, pk):
        player = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(player)
        return Response(serializer.data)

    # удалить игрока (для модератора)
    def delete(self, request, pk):

        # if not request.user.is_staff:
        #     return Response(status=status.HTTP_403_FORBIDDEN)

        player = get_object_or_404(self.model_class, pk=pk)
        player.status = 'deleted'
        player.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # добавить нового игрока (для модератора)
    def post(self, request, format=None):
        # if not request.user.is_staff:
        #     return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # обновление игрока (для модератора)
    def put(self, request, pk, format=None):

        # if not request.user.is_staff:
        #     return Response(status=status.HTTP_403_FORBIDDEN)

        player = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(player, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddPlayerView(APIView):
    # добавление услуги в заявку
    def post(self, request):
        # создаем заявку, если ее еще нет
        if not Team.objects.filter(user=request.user, status='draft').exists():
            new_team = Team()
            new_team.user = request.user
            new_team.save()

        team_id = Team.objects.filter(user=request.user, status='draft').first().id
        serializer = TeamPlayerSerializer(data=request.data)
        if serializer.is_valid():
            new_team_player = TeamPlayer()
            new_team_player.player_id = serializer.validated_data["player_id"]
            new_team_player.team_id = team_id
            if 'is_captain' in request.data:
                new_team_player.is_captain = request.data["is_captain"]
            new_team_player.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageView(APIView):
    def post(self, request):
        # if not request.user.is_staff:
        #    return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = AddImageSerializer(data=request.data)
        if serializer.is_valid():
            player = Player.objects.get(pk=serializer.validated_data['player_id'])
            player.image_player_url = serializer.validated_data['image_player_url']
            player.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# USER VIEWS
class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Личный кабинет (обновление профиля)
class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserUpdateSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Аутентификация пользователя
class UserLoginView(APIView):
    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Деавторизация пользователя
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()  # Удаляем токен
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListTeams(APIView):
    def get(self, request):
        if 'date' in request.data and 'status' in request.data:
            teams = Team.objects.filter(updated_at__gte=request.data['date'], status=request.data['status']).exclude(
                updated_at=None)
        else:
            teams = Team.objects.all()

        teams_serializer = TeamSerializer(teams, many=True)
        return Response(teams_serializer.data, status=status.HTTP_200_OK)


class GetTeam(APIView):
    def get(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        serializer = TeamSerializer(team)

        team_players = TeamPlayer.objects.filter(team=team)
        player_ids = []
        for team_player in team_players:
            player_ids.append(team_player.player_id)

        player_in_team = []
        for id in player_ids:
            player_in_team.append(get_object_or_404(Player, pk=id))

        players_serializer = PlayerListSerializer(player_in_team, many=True)
        response = serializer.data
        response['players'] = players_serializer.data

        return Response(response, status=status.HTTP_200_OK)

    def put(self, request, pk):
        serializer = PutTeamSerializer(data=request.data)
        if serializer.is_valid():
            team = get_object_or_404(Team, pk=pk)
            # animal.type = serializer.validated_data['type']
            # animal.genus = serializer.validated_data['genus']
            for attr, value in serializer.validated_data.items():
                setattr(team, attr, value)
            team.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FormTeam(APIView):
    def put(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        if not team.status == 'draft':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # if not request.user == req.user:
        #    return Response(status=status.HTTP_403_FORBIDDEN)

        # if animal.created_at > datetime.now():
        #     return Response(status=status.HTTP_400_BAD_REQUEST)

        if not team.completed_at == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        team.updated_at = datetime.now()
        team.status = 'formed'
        team.save()
        return Response(status=status.HTTP_200_OK)


class ModerateTeam(APIView):
    def put(self, request, pk):

        # if not request.user.is_staff:
        #    return Response(status=status.HTTP_403_FORBIDDEN)

        team = get_object_or_404(Team, pk=pk)
        serializer = AcceptTeamSerializer(data=request.data)
        if not team.status == 'formed':
            return Response({'error': 'Заявка не сформирована'}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            if serializer.validated_data['accept'] == True and team.status:
                team.status = 'completed'
                team.moderator = request.user


            else:
                team.status = 'cancelled'
                team.moderator = request.user
                team.completed_at = datetime.now()
            team.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        team = get_object_or_404(Team, pk=pk)

        # TODO auth
        # if not request.user.is_staff or not request.user == Request:
        #    return Response(status=status.HTTP_403_FORBIDDEN)

        team.status = 'deleted'
        team.ended_at = datetime.now()
        team.save()
        return Response(status=status.HTTP_200_OK)


class EditTeamPlayer(APIView):
    def delete(self, request, pk):
        if 'player_id' in request.data:
            record_m_to_m = get_object_or_404(TeamPlayer, team=pk, player=request.data['player_id'])
            record_m_to_m.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        # if not request.user.is_staff:
        #     return Response(status=status.HTTP_403_FORBIDDEN)
        if 'player_id' in request.data and 'is_captain' in request.data:
            record_m_to_m = get_object_or_404(TeamPlayer, team=pk, player=request.data['player_id'])
            record_m_to_m.is_captain = request.data['is_captain']
            record_m_to_m.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)