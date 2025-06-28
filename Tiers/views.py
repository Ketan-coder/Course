from utils.models import Activity
from .models import LeaderboardEntry, Tournament, Tier, TierRank
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Users.models import Profile

@login_required
def tournament_detail_view(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    profile = Profile.objects.get(user=request.user)

    has_joined = tournament.participants.filter(id=profile.id).exists()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "join" and not has_joined:
            tournament.participants.add(profile)

            # Auto-create LeaderboardEntry if not exists
            LeaderboardEntry.objects.get_or_create(profile=profile, tournament=tournament)
            Activity.objects.create(
                user=request.user,
                activity_type='Tournament Join',
                description=f"Joined tournament: {tournament.name}",
            ) 

            messages.success(request, f"You’ve successfully joined the tournament: {tournament.name}")
            return redirect('tournament_detail', pk=pk)

        elif action == "leave" and has_joined:
            tournament.participants.remove(profile)

            # Optionally delete leaderboard entry
            LeaderboardEntry.objects.filter(profile=profile, tournament=tournament).delete()
            Activity.objects.create(
                user=request.user,
                activity_type='Tournament Leave',
                description=f"Left tournament: {tournament.name}",
            )

            messages.warning(request, f"You’ve left the tournament: {tournament.name}")
            return redirect('tournament_detail', pk=pk)

    context = {
        'tournament': tournament,
        'has_joined': has_joined
    }
    return render(request, 'tiers/tournament_detail.html', context)


def leaderboard_view(request):
    tournament_id = request.GET.get('tournament', None)
    tournaments = Tournament.objects.all().order_by('-start_date')

    if tournament_id:
        selected_tournament = Tournament.objects.filter(id=tournament_id).first()
        entries = LeaderboardEntry.objects.filter(tournament=selected_tournament).order_by('-score', 'timestamp') if selected_tournament else []
    else:
        selected_tournament = None
        entries = LeaderboardEntry.objects.all().order_by('-score', 'timestamp')

    context = {
        'entries': entries,
        'selected_tournament': selected_tournament,
        'tournaments': tournaments,
    }
    return render(request, 'tiers/leaderboard.html', context)

def update_leaderboard_score(profile, tournament, new_score):
    entry, created = LeaderboardEntry.objects.get_or_create(profile=profile, tournament=tournament)
    entry.score = new_score
    entry.save()

@login_required
def tiers_view(request):
    profile = Profile.objects.get(user=request.user)

    # Get current score (latest tournament or overall)
    entry = LeaderboardEntry.objects.filter(profile=profile).order_by('-timestamp').first()
    user_score = entry.score if entry else 0

    # Find the highest Tier the user qualifies for
    user_tier = Tier.objects.filter(min_score__lte=user_score).order_by('-min_score').first()

    tiers = Tier.objects.prefetch_related('ranks').all()

    context = {
        'tiers': tiers,
        'user_tier': user_tier,
        'user_score': user_score
    }
    
    next_tier = Tier.objects.filter(min_score__gt=user_score).order_by('min_score').first()

    if next_tier:
        score_diff = next_tier.min_score - user_score
        total_needed = next_tier.min_score - (user_tier.min_score if user_tier else 0)
        progress_percent = int((user_score - (user_tier.min_score if user_tier else 0)) / total_needed * 100)
    else:
        score_diff = 0
        progress_percent = 100  # max tier

    context.update({
        'next_tier': next_tier,
        'progress_percent': progress_percent,
        'score_needed': score_diff
    })

    return render(request, 'tiers/tiers.html', context)