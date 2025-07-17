from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Course, Quiz


@receiver(post_save, sender=Quiz)
def reward_quiz_completion(sender, instance, created, **kwargs):
    if not created:
        pass
