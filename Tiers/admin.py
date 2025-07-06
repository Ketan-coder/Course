from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Tier)
admin.site.register(TierRank)

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'start_date', 'end_date')
    list_filter = ('is_active',)

@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ('profile', 'tournament', 'score', 'timestamp')
    list_filter = ('tournament',)