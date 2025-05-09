from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
# from CourseApp.utils import send_email
from .models import Profile
import uuid

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance, email_confirmation_token=uuid.uuid4())
        # send_email(
        #     to_email=instance.email,
        #     subject="Confirm Your Email",
        #     title="Confirm Email",
        #     body=f"Hi {instance.username}, click the button below to verify your email.",
        #     anchor_link=f"https://sajangiri.pythonanywhere.com/accounts/confirm/{profile.email_confirmation_token}/",            
        #     anchor_text="Confirm Email"
        # )

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(pre_delete, sender=User)
def delete_profile(sender, instance, **kwargs):
    instance.profile.delete()