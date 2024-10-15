# Generated by Django 4.2.4 on 2024-10-14 13:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('active', 'действует'), ('deleted', 'удален')], default='active', max_length=15)),
                ('f_name', models.CharField(max_length=30)),
                ('l_name', models.CharField(max_length=30)),
                ('image_player_url', models.URLField()),
                ('date_birthday', models.DateField()),
                ('weight', models.IntegerField(max_length=10)),
                ('height', models.IntegerField(max_length=10)),
                ('position', models.CharField(max_length=30)),
                ('number', models.IntegerField(max_length=10)),
                ('birth_place', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'players',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_team', models.CharField(max_length=100)),
                ('competition', models.CharField(max_length=30)),
                ('date_competition', models.DateField(null=True)),
                ('status', models.CharField(choices=[('draft', 'черновик'), ('formed', 'сформирован'), ('completed', 'завершён'), ('cancelled', 'отклонен'), ('deleted', 'удален')], default='draft', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('moderator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='moderator_id', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'teams',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TeamPlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_captain', models.BooleanField(default=False, null=True)),
                ('player', models.ForeignKey(max_length=10, on_delete=django.db.models.deletion.CASCADE, to='team.player')),
                ('team', models.ForeignKey(max_length=10, on_delete=django.db.models.deletion.CASCADE, related_name='team_players', to='team.team')),
            ],
            options={
                'db_table': 'players_teams',
                'managed': True,
            },
        ),
        migrations.AddConstraint(
            model_name='teamplayer',
            constraint=models.UniqueConstraint(fields=('player', 'team'), name='unique_player_team'),
        ),
    ]
