from django.shortcuts import render
from django.shortcuts import redirect
from django.db import connection
from .models import Player, Team, TeamPlayer
from django.contrib.auth.models import User


def home(request):
    if not Team.objects.filter(status='draft').exists():
        player_count = 0
        current_request = 0
    else:
        team = Team.objects.filter(status='draft')
        current_request = team.first()
        player_count = current_request.team_players.count()

    player_name = request.GET.get('last_name', '')
    if player_name:
        players = Player.objects.filter(l_name__icontains=player_name)
    else:
        players = Player.objects.all()

    return render(request, 'app/index.html', {'data': {
        'players': players,
        'count_pls': player_count,
        'team_id': current_request.id if current_request else 0
    }})


def player(request, id):
    current_player = Player.objects.get(id=id)
    return render(request, 'app/players.html', {'current_player': current_player})


def basket(request, id):
    if id == 0:
        return render(request, 'app/basket.html', {'current_request': None})

    if Team.objects.filter(id=id).exclude(status='draft').exists():
        return render(request, 'app/basket.html', {'current_request': None})

    if not Team.objects.filter(id=id).exists():
        return render(request, 'app/basket.html', {'current_request': None})

    req_id = id
    current_request = Team.objects.get(id=id)
    players_ids = TeamPlayer.objects.filter(team=current_request).values_list('player_id', flat=True)
    current_players = Player.objects.filter(id__in=players_ids)

    return render(request, 'app/basket.html', {'data': {
        'current_players': current_players,
        'current_request': current_request,
        'req_id': req_id
    }})


def add_player(request):
    if request.method == 'POST':
        if not Team.objects.filter(status='draft').exists():
            team = Team()
            team.user_id = request.user.id
            team.save()
        else:
            team = Team.objects.get(status='draft')

        player_id = request.POST.get('player_id')
        new_player = Player.objects.get(id=player_id)
        if TeamPlayer.objects.filter(team=team, player=new_player).exists():
            return redirect('/')
        team_player = TeamPlayer(team=team, player=new_player)
        team_player.save()
        return redirect('/')
    else:
        return redirect('/')


def del_team(request):
    if request.method == 'POST':
        team_id = request.POST.get('team_id')
        with connection.cursor() as cursor:
            cursor.execute("UPDATE teams SET status = %s WHERE id = %s", ['deleted', team_id])
        return redirect('/')
    else:
        return redirect('/')