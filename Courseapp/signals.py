from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Course, Quiz, QuizSubmission


from django.contrib.auth.models import User

@receiver(post_save, sender=Quiz)
def quiz_completion(sender, instance, created, **kwargs):
    request = kwargs.get('request')
    if request and not created:
        question_count = len(instance.questions or {})
        completed_count = sum(1 for qid, qdata in (instance.questions or {}).items() if qdata["is_completed"] == True)
        total_earned_points = sum(qdata["score_on_completion"] for qid, qdata in (instance.questions or {}).items() if qdata["is_completed"] == True)
        if question_count != 0 and question_count == completed_count:
            profile = User.objects.get(id=request.user.id).profile
            QuizSubmission.objects.create(
                quiz_id=instance.id,
                user=profile,
                score=total_earned_points,
                total=total_earned_points,
                passed=True,
                answers=instance.questions
            )

