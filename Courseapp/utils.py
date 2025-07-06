import datetime
from django.utils import timezone
from Users.models import Student
from django.db import transaction
from Tiers.models import LeaderboardEntry
from django.contrib import messages
from utils.models import Activity

@transaction.atomic
def update_streak(request,profile):
    """
    Update the user's streak count when they complete a lesson.
    Resets the streak if it's their first lesson of the day,
    or increments if they're continuing their streak.
    Atomic transaction ensures data consistency.
    """
    try:
        student_profile = Student.objects.get(profile=profile)
        today = timezone.now().date()
        last_updated = student_profile.streak_last_updated_date.date()
        
        # Already updated today - no action needed
        if last_updated == today:
            return
        
        days_missed = (today - last_updated).days - 1
        
        # Perfect consecutive day (yesterday)
        if days_missed == 0:
            student_profile.streak += 1
            student_profile.streak_last_updated_date = timezone.now()
            student_profile.save()
            Activity.objects.create(
                user=profile.user,
                activity_type="Streak",
                description=f"Streak is incremented to {student_profile.streak}",
            )
            return
        
        # Missed one day but has freezes available
        elif days_missed == 1 and student_profile.streak_freezes > 0:
            student_profile.streak += 1
            student_profile.streak_freezes -= 1
            student_profile.streak_last_updated_date = timezone.now()
            student_profile.save()
            return
        
        elif days_missed == 2 and student_profile.streak_freezes > 1:
            student_profile.streak += 1
            student_profile.streak_freezes -= 1
            student_profile.streak_last_updated_date = timezone.now()
            student_profile.save()
            return
        
        # Missed more than one day or no freezes available
        else:
            student_profile.streak = 1  # Reset to 1 for today's completion
            student_profile.streak_last_updated_date = timezone.now()
            student_profile.save()
            return
        
    except Student.DoesNotExist:
        messages.error(request, "Instructor Doesn't have streaks")


@transaction.atomic
def update_score(request,profile, increment_score_by=10):
    """
    Updates the user's score and potentially awards bonus points for streaks.
    Atomic transaction ensures data consistency.
    """
    try:
        student_profile = Student.objects.get(profile=profile)
        leaderboard_student_profile = LeaderboardEntry.objects.get(profile=profile)
        
        # Update basic score
        student_profile.score += increment_score_by
        leaderboard_student_profile.score += increment_score_by
        
        # Check for streak bonus (example: 10% bonus for 7+ day streaks)
        if student_profile.streak >= 7:
            bonus = int(increment_score_by * 0.1)  # 10% bonus
            student_profile.score += bonus
            leaderboard_student_profile.score += bonus
            # student_profile.bonus_points_earned += bonus

            Activity.objects.create(
                user=profile.user,
                activity_type="Bouns Points Earned",
                description=f"Bouns Points Earned: {bonus} - Final Score is: {student_profile.score}",
            )
        
        # Daily score cap (prevent abuse)
        today = timezone.now().date()
        if student_profile.last_score_update.date() != today:
            student_profile.daily_score = 0
            student_profile.last_score_update = timezone.now()
        
        MAX_DAILY_SCORE = 100
        if (student_profile.daily_score + increment_score_by) > MAX_DAILY_SCORE:
            remaining = MAX_DAILY_SCORE - student_profile.daily_score
            student_profile.score += remaining
            leaderboard_student_profile.score += remaining
            student_profile.daily_score = MAX_DAILY_SCORE
        else:
            student_profile.daily_score += increment_score_by
        
        student_profile.save()
        leaderboard_student_profile.save()
        
        # Return points actually added (considering caps and bonuses)
        actual_points_added = increment_score_by
        if student_profile.streak >= 7:
            actual_points_added += bonus
        
        return actual_points_added
        
    except Student.DoesNotExist:
        messages.error(request, "Instructor Doesn't have scores")