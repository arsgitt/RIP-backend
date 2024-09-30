from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Player
from .models import Team
from .models import TeamPlayer

# Register your models here.
admin.site.register(Player)
admin.site.register(Team)

@admin.register(TeamPlayer)
class TeamPlayerAdmin(admin.ModelAdmin):
    list_display = ('team_id', 'player_id')
    search_fields = ('team_id', 'player_id')