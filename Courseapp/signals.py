from django.db.models.signals import post_save, m2m_changed
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Course, Quiz, QuizSubmission, Lesson, Section
from django.db.models import Sum, Q
from django.db import transaction
from Users.models import Profile, Student
from utils.utils import generate_unique_code
from .utils import has_completed_course, generate_certificate

@receiver(post_save, sender=Quiz)
def quiz_completion(sender, instance, created, **kwargs):
    request = kwargs.get('request')
    if request and not created:
        question_count = len(instance.questions or {})
        completed_count = sum(1 for qid, qdata in (instance.questions or {}).items() if qdata["is_completed"] == True)
        total_earned_points = sum(qdata["score_on_completion"] for qid, qdata in (instance.questions or {}).items() if qdata["is_completed"] == True)
        if question_count != 0 and question_count == completed_count and total_earned_points > 0:
            with transaction.atomic():
                profile = User.objects.get(id=request.user.id).profile
                QuizSubmission.objects.create(
                    quiz_id=instance.id,
                    user=profile,
                    score=total_earned_points,
                    total=total_earned_points,
                    passed=True if total_earned_points >= instance.passing_marks else False,
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
                total_score += int(q_data.get('score_on_completion', 0) or 0)

    if instance.is_class_room_course:
        instance.course_code = generate_unique_code()

    if instance.extra_fields.get('score_on_completion') != total_score:
        instance.extra_fields['score_on_completion'] = total_score
        Course.objects.filter(pk=instance.pk).update(extra_fields=instance.extra_fields, course_code=instance.course_code)


# check if all lessons and quizes from that course is completed then generate a certificate for that student
@receiver(post_save, sender=QuizSubmission)
def check_quiz_completion(sender, instance, created, **kwargs):
    try:
        print("Checking quiz completion")
        profile = instance.user
        
        course = ''
        
        if instance.quiz.section:
            section = instance.quiz.section
            course = Course.objects.filter(sections=section).first()
        elif instance.quiz.course:
            course = instance.quiz.course
        elif instance.quiz.lesson:
            lesson = instance.quiz.lesson
            section = Section.objects.filter(lesson=lesson).first()
            course = Course.objects.filter(sections=section).first()
        
        student = Student.objects.filter(profile=profile).first()

        if not course:
            print("No course for quiz completion")
            return
        
        if not student:
            print("No student for quiz completion")
            return

        if has_completed_course(course, profile) and student:
            print("Generating certificate")
            generate_certificate(course, profile)
    except Exception as e:
        print("Error in quiz completion:", e)

@receiver(m2m_changed, sender=Lesson.completed_by_users.through)
def check_lesson_completion(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        profile_id = list(pk_set)[0]
        print("Profile ID:", profile_id)
        profile = Profile.objects.get(id=profile_id)
        # course = Course.objects.filter(sections__lesson=instance).first()
        lesson = instance.pk
        section = Section.objects.filter(lesson=lesson).first()
        course = Course.objects.filter(sections=section).first()
        student = Student.objects.filter(profile=profile).first()

        if course and has_completed_course(course, profile) and student:
            generate_certificate(course, profile)
