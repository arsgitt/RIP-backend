from django.db.models import F
from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import SessionAuthentication

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
from django.contrib.auth import logout, login
from datetime import datetime


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class PlayerList(APIView):
    model_class = Player
    serializer_class = PlayerListSerializer

    @swagger_auto_schema(
        operation_description="Получение списка игроков. Можно отфильтровать по его фамилии.",
        manual_parameters=[
            openapi.Parameter('l_name', openapi.IN_QUERY, description="Фамилия игрока",
                              type=openapi.TYPE_STRING, default=""),
        ],
        responses={200: PlayerListSerializer(many=True)}
    )
    def get(self, request):
        if 'l_name' in request.GET:
            players = self.model_class.objects.filter(l_name__icontains=request.GET['l_name'])
        else:
            players = self.model_class.objects.all()

        serializer = self.serializer_class(players, many=True)
        resp = serializer.data
        if request.user.is_authenticated:
            draft_request = Team.objects.filter(user=request.user, status='draft').first()
            draft_request_id = Team.objects.filter(user=request.user, status='draft').first().id
            count_players_in_draft = TeamPlayer.objects.filter(team=draft_request).values_list('player_id',
                                                                                                     flat=True).count()
        else:
            draft_request_id = None
            count_players_in_draft = None


        resp.append({'draft_request_id': draft_request_id})  # Use RequestSerializer here
        resp.append({'count': count_players_in_draft})

        return Response(resp, status=status.HTTP_200_OK)


class PlayerDetail(APIView):
    model_class = Player
    serializer_class = PlayerDetailSerializer

    @swagger_auto_schema(
        operation_description="Получить информацию о конкретном игроке по ID.",
        responses={200: PlayerDetailSerializer()}
    )
    # получить игрока
    def get(self, request, pk):
        player = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(player)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Удаление игрока по ID (moderators only).",
        responses={204: 'No Content', 403: 'Forbidden'}
    )
    # удалить игрока (для модератора)
    def delete(self, request, pk):

        # if not request.user.is_staff:
        #     return Response(status=status.HTTP_403_FORBIDDEN)

        player = get_object_or_404(self.model_class, pk=pk)
        player.status = 'deleted'
        player.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="Добавление нового игрока (moderators only).",
        request_body=PlayerDetailSerializer,
        responses={201: PlayerDetailSerializer(), 400: 'Bad Request'}
    )
    # добавить нового игрока (для модератора)
    def post(self, request, format=None):
        # if not request.user.is_staff:
        #     return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Обновление данных игрока (moderators only).",
        request_body=PlayerDetailSerializer,
        responses={200: PlayerDetailSerializer(), 400: 'Bad Request'}
    )
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
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    # добавление услуги в заявку
    @swagger_auto_schema(
        operation_description="Добавление игрока в заявку-черновик пользователя. Создается новая заявка, если не существует заявки-черновика",
        responses={200: "Игрок успешно добавлен в заявку", 404: "Игрок не найден"},
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, description="Номер игрока", type=openapi.TYPE_INTEGER,
                              required=True)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'is_captain': openapi.Schema(type=openapi.TYPE_NUMBER, description='Капитан?',
                                             example=1)},
            required=[]
        )
    )
    # добавление услуги в заявку
    def post(self, request, pk):
        # создаем заявку, если ее еще нет
        if not Team.objects.filter(user=request.user, status='draft').exists():
            new_team = Team()
            new_team.user = request.user
            new_team.username = request.user.username
            new_team.save()

        team_id = Team.objects.filter(user=request.user, status='draft').first().id
        if Player.objects.filter(pk=pk).exists():
            new_team_player = TeamPlayer()
            new_team_player.player_id = pk
            new_team_player.team_id = team_id
            if 'is_captain' in request.data:
                new_team_player.is_captain = request.data["is_captain"]
            new_team_player.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({'error':'threat not found'}, status=status.HTTP_400_BAD_REQUEST)


class ImageView(APIView):
    @swagger_auto_schema(
        operation_description="Upload an image for a specific threat.",
        request_body=AddImageSerializer,
        responses={201: "Image uploaded successfully", 400: "Bad request"}
    )
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
    @swagger_auto_schema(
        operation_description="Регистрация нового пользователя.",
        request_body=UserRegistrationSerializer,
        responses={201: "User registered successfully", 400: "Bad request"}
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Личный кабинет (обновление профиля)
class UserUpdateView(APIView):
    permission_classes = [CsrfExemptSessionAuthentication]

    @swagger_auto_schema(
        operation_description="Обновление профиля аунтифицированного пользователя",
        request_body=UserUpdateSerializer,
        responses={200: UserUpdateSerializer(), 400: "Bad request"}
    )
    def put(self, request):
        serializer = UserUpdateSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Аутентификация пользователя
class UserLoginView(APIView):
    @swagger_auto_schema(
        operation_description="Аунтификация пользователя с логином и паролем. Возвращает файл cookie сеанса в случае успеха.",
        request_body=AuthTokenSerializer,
        responses={200: "Login successful", 400: "Invalid credentials"}
    )
    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            username = request.data['username']
            password = request.data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)  # Сохраняем информацию о пользователе в сессии
                # random_key = uuid.uuid4()
                # session_storage.set(random_key, username)
                return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Деавторизация пользователя
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Выход аунтифицированного пользователя. Удаление сессии.",
        responses={204: "Logout successful"}
    )
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_204_NO_CONTENT)


class ListTeams(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a list of requests. Optionally filter by date and status.",
        manual_parameters=[
            openapi.Parameter('date', openapi.IN_QUERY, description="Filter requests after a specific date",
                              type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter requests by status",
                              type=openapi.TYPE_STRING)
        ],
        responses={200: TeamSerializer(many=True)}
    )
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_staff:
                if 'date' in request.data and 'status' in request.data:
                    teams = Team.objects.filter(updated_at__gte=request.data['date'],
                                                status=request.data['status']).exclude(
                        updated_at=None)
                else:
                    teams = Team.objects.exclude(
                        updated_at=None)
                    teams_serializer = TeamSerializer(teams, many=True)
                    return Response(teams_serializer.data, status=status.HTTP_200_OK)


            else:
                if 'date' in request.data and 'status' in request.data:
                    teams = Team.objects.filter(user=request.user, updated_at__gte=request.data['date'],
                                                status=request.data['status']).exclude(
                        updated_at=None)
                else:
                    teams = Team.objects.filter(user=request.user).exclude(
                        updated_at=None)
                    teams_serializer = TeamSerializer(teams, many=True)
                    return Response(teams_serializer.data, status=status.HTTP_200_OK)

        else:
            return Response({'message': 'Вы не вошли в аккаунт'}, status=status.HTTP_403_FORBIDDEN)


class GetTeam(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get details of a request by ID, including associated threats.",
        responses={200: TeamSerializer()}
    )
    def get(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        serializer = TeamSerializer(team)
        response = serializer.data

        current_players = Player.objects.filter(
            player_player__team=pk  # Проверка на соответствие стоянки
        ).annotate(
            is_captain=F('player_player__is_captain')  # Добавляем информацию о капитане из модели ParkingShip
        ).order_by('id')

        players_serializer = PlayerListInTeamSerializer(current_players, many=True)
        response['players'] = players_serializer.data

        return Response(response, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a request by ID.",
        request_body=PutTeamSerializer,
        responses={200: "Request updated successfully", 400: "Bad request"}
    )
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
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Mark a request as formed. Only available for requests with a 'draft' status.",
        responses={200: "Request successfully formed", 400: "Bad request"}
    )
    def put(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        if not team.status == 'draft':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not request.user == team.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # if animal.created_at > datetime.now():
        #     return Response(status=status.HTTP_400_BAD_REQUEST)

        if not team.completed_at == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        team.updated_at = datetime.now()
        team.status = 'formed'
        team.save()
        return Response(status=status.HTTP_200_OK)


class ModerateTeam(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Approve or decline a request (for moderators).",
        request_body=AcceptTeamSerializer,
        responses={200: "Request moderated successfully", 400: "Bad request"}
    )
    def put(self, request, pk):

        if not request.user.is_staff:
            return Response({'error': 'Вы не можете модерировать заявку'}, status=status.HTTP_403_FORBIDDEN)

        team = get_object_or_404(Team, pk=pk)
        serializer = AcceptTeamSerializer(data=request.data)
        if not team.status == 'formed':
            return Response({'error': 'Заявка не сформирована'}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            if serializer.validated_data['accept'] == True and team.status:
                team.status = 'completed'
                team.moderator = request.user
                team.completed_at = datetime.now()


            else:
                team.status = 'cancelled'
                team.moderator = request.user
                team.completed_at = datetime.now()

            team.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a request (for moderators).",
        responses={200: "Request deleted successfully"}
    )

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
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Remove a threat from a request.",
        # request_body=openapi.Schema(
        #     type=openapi.TYPE_OBJECT,
        #     properties={'threat_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the threat")},
        #     required=['threat_id']
        # ),
        responses={200: "Threat removed successfully", 400: "Bad request"}
    )
    def delete(self, request, player_pk, team_pk):
        # if 'player_id' in request.data:
        #     record_m_to_m = get_object_or_404(TeamPlayer, team=team_pk, player=player_pk)
        #     record_m_to_m.delete()
        #     return Response(status=status.HTTP_200_OK)
        # else:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        record_m_to_m = get_object_or_404(TeamPlayer, team=team_pk, player=player_pk)
        record_m_to_m.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update the price of a threat in a request.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'is_captain': openapi.Schema(type=openapi.TYPE_NUMBER, description="Капитан команды")
            },
            required=['is_captain']
        ),
        responses={200: "captain updated successfully", 400: "Bad request"}
    )
    def put(self, request, player_pk, team_pk):
        # if not request.user.is_staff:
        #     return Response(status=status.HTTP_403_FORBIDDEN)
        if 'is_captain' in request.data:
            record_m_to_m = get_object_or_404(TeamPlayer, team=team_pk, player=player_pk)
            record_m_to_m.is_captain = request.data['is_captain']
            record_m_to_m.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)