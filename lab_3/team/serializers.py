from .models import Player, Team, TeamPlayer
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class AddImageSerializer(serializers.Serializer):
    player_id = serializers.IntegerField(required=True)
    image_player_url = serializers.CharField(required=True)

    def validate(self, data):
        player_id = data.get('player_id')

        # Дополнительная логика валидации, например проверка на существование этих id в базе данных
        if not Player.objects.filter(pk=player_id).exists():
            raise serializers.ValidationError(f"player_id is incorrect")

        return data


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["pk","name_team", "competition", "date_competition", "status", "created_at", "updated_at", "completed_at", "user",
                  "moderator"]


class PutTeamSerializer(serializers.ModelSerializer):
    competition = serializers.CharField()
    name_team = serializers.CharField()
    date_competition = serializers.DateField()

    class Meta:
        model = Team
        fields = ["name_team", "competition", "date_competition", "status", "created_at", "updated_at", "completed_at", "user",
                  "moderator"]


class PlayerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["pk","status", "f_name", "l_name", "image_player_url", "date_birthday", "weight", "height", "position",
                  "number", "birth_place"]


class PlayerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["pk", "status", "f_name", "l_name", "image_player_url", "date_birthday", "weight", "height", "position",
                  "number", "birth_place"]


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["pk", "image_player_url"]


class TeamPlayerSerializer(serializers.Serializer):
    player_id = serializers.IntegerField(required=True)
    is_captain = serializers.BooleanField(required=False)

    def validate(self, data):
        player_id = data.get('player_id')

        # Дополнительная логика валидации, например проверка на существование этих id в базе данных
        if not Player.objects.filter(id=player_id).exists():
            raise serializers.ValidationError(f"player_id is incorrect")

        return data


# AUTH SERIALIZERS

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Неверные учетные данные")
        return {'user': user}


class CheckUsernameSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate(self, data):
        if not User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Пользователь не существует")

        return data


class AcceptTeamSerializer(serializers.Serializer):
    accept = serializers.BooleanField()