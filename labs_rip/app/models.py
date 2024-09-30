from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User




class Player(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "действует"
        DELETED = "deleted", "удален"

    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)

    f_name = models.CharField(max_length=30)
    l_name = models.CharField(max_length=30)
    biography = models.CharField(null=True)
    image_player_url = models.URLField()
    date_birthday = models.DateField()
    weight = models.IntegerField(max_length=10)
    height = models.IntegerField(max_length=10)
    position = models.CharField(max_length=30)
    number = models.IntegerField(max_length=10)
    country = models.CharField(max_length=30)
    img_country_url = models.URLField()
    birth_place = models.CharField(max_length=30)

    class Meta:
        managed = True
        db_table = 'players'


class Team(models.Model):
    competition = models.CharField(max_length=30)
    date_competition = models.DateField(null=True)

    class Status(models.TextChoices):
        DRAFT = "draft", "черновик"
        FORMED = "formed", "сформирован"
        COMPLETED = "completed", "завершён"
        CANCELLED = "cancelled", "отклонен"
        DELETED = "deleted", "удален"
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    moderator = models.ForeignKey(User, null=True, related_name='moderator_id', on_delete=models.CASCADE)
    class Meta:
        managed = True
        db_table = 'teams'


class TeamPlayer(models.Model):
    player = models.ForeignKey(Player, max_length=10, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, max_length=10, on_delete=models.CASCADE,related_name='team_players')
    is_captain = models.BooleanField(null=True)

    class Meta:
        managed = True
        db_table = 'players_teams'
        constraints = [
            models.UniqueConstraint(fields=['player', 'team'], name='unique_player_team')
        ]


