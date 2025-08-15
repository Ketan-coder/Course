from django.db import models

class CourseManager(models.Manager):
    """
    Change the queryset to exclude deleted courses
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class SectionManager(models.Manager):
    """
    Change the queryset to exclude deleted sections
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class LessonManager(models.Manager):
    """
    Change the queryset to exclude deleted lessons
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class QuizManager(models.Manager):
    """
    Change the queryset to exclude deleted quizzes
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class TagManager(models.Manager):
    """
    Change the queryset to exclude deleted tags
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class ArticleManager(models.Manager):
    """
    Change the queryset to exclude deleted articles
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)