from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Course, Quiz, QuizSubmission
from django.db.models import Sum, Q
from django.db import transaction
from django.contrib.auth.models import User
from utils.utils import generate_unique_code

@receiver(post_save, sender=Quiz)
def quiz_completion(sender, instance, created, **kwargs):
    request = kwargs.get('request')
    if request and not created:
        question_count = len(instance.questions or {})
        completed_count = sum(1 for qid, qdata in (instance.questions or {}).items() if qdata["is_completed"] == True)
        total_earned_points = sum(qdata["score_on_completion"] for qid, qdata in (instance.questions or {}).items() if qdata["is_completed"] == True)
        if question_count != 0 and question_count == completed_count:
            with transaction.atomic():
                profile = User.objects.get(id=request.user.id).profile
                QuizSubmission.objects.create(
                    quiz_id=instance.id,
                    user=profile,
                    score=total_earned_points,
                    total=total_earned_points,
                    passed=True,
                    answers=instance.questions
                )
                for qid, qdata in (instance.questions or {}).items():
                    qdata["is_completed"] = False
                    instance.questions[qid] = qdata
                instance.save()

@receiver(post_save, sender=Course)
def update_earn_points(sender, instance, created, **kwargs):
    section_ids = instance.sections.all().values_list('id', flat=True)

    linked_quizzes = Quiz.objects.filter(
        Q(course_id=instance.id) | Q(section_id__in=section_ids)
    )

    total_score = 0

    for quiz in linked_quizzes:
        if isinstance(quiz.questions, dict):
            for q_id, q_data in quiz.questions.items():
                total_score += q_data.get('score_on_completion', 0)

    if instance.is_class_room_course:
        instance.course_code = generate_unique_code()

    if instance.extra_fields.get('score_on_completion') != total_score:
        instance.extra_fields['score_on_completion'] = total_score
        Course.objects.filter(pk=instance.pk).update(extra_fields=instance.extra_fields, course_code=instance.course_code)
