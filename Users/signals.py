from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from utils.utils import send_email_using_resend
import uuid
from .models import Instructor, Profile, Student
import datetime
from Stock.models import Wallet, StockPortfolio
from django.conf import settings

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance, email_confirmation_token=uuid.uuid4())
        wallet = Wallet.objects.create(user=profile, balance=10000)
        stock_portfolio = StockPortfolio.objects.create(user=profile)
        send_email_using_resend(
            to_email=instance.email,
            subject="Confirm Your Email",
            title="Confirm Email",
            body=f"Hi {instance.username}, click the button below to verify your email.",
            anchor_link=f"https://{settings.SITE_URL}/accounts/confirm/{profile.email_confirmation_token}/",            
            anchor_text="Confirm Email"
        )

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(pre_delete, sender=User)
def delete_profile(sender, instance, **kwargs):
    instance.profile.delete()

@receiver(post_save, sender=User)
def update_profile_on_user_save(sender, instance, **kwargs):
    try:
        profile = Profile.objects.get(user=instance)
        profile.extra_fields['last_logged_in'] = str(instance.last_login) if instance.last_login else None
        profile.extra_fields['is_active'] = instance.is_active
        profile.extra_fields['date_joined'] = instance.date_joined.strftime('%Y-%m-%d %H:%M:%S') if instance.date_joined else None
        profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Profile)
def update_profile_extra_fields_on_save(sender, instance, **kwargs):
    instance.extra_fields['whole_phone_no'] = instance.phone_no_prefix.phone_no_prefix + instance.phone_no if instance.phone_no_prefix and instance.phone_no else None
    if instance.date_of_birth:
        # Use timezone.now().date() for current date to avoid naive datetime issues
        from django.utils import timezone
        age = (timezone.now().date() - instance.date_of_birth).days // 365
        instance.extra_fields['age'] = age
    else:
        instance.extra_fields['age'] = None
    # Only save if extra_fields has changed to avoid potential infinite loops
    # if instance.has_changed('extra_fields'):
    #     instance.save()

@receiver(post_save, sender=User)
def create_instructor_on_user_save(sender, instance, created, **kwargs):
    if created:
        try:
            Profile.objects.get(user=instance)
            Student.objects.create(profile=Profile.objects.get(user=instance))
        except Profile.DoesNotExist:
            pass # Profile will be created by its own signal

@receiver(post_save, sender=Profile)
def update_instructor_on_profile_save(sender, instance, **kwargs):
    try:
        instructor = Instructor.objects.get(profile=instance)
        instructor.extra_fields['last_logged_in'] = str(instance.user.last_login) if instance.user.last_login else None
        instructor.extra_fields['is_active'] = instance.user.is_active
        instructor.extra_fields['date_joined'] = instance.user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if instance.user.date_joined else None
        instructor.extra_fields['full_name'] = f"{instance.user.first_name} {instance.user.last_name}".strip()
        # Only save if extra_fields has changed
        # if instructor.has_changed('extra_fields'):
        #     instructor.save()
    except Instructor.DoesNotExist:
        pass

@receiver(post_save, sender=User)
def update_student_on_user_save(sender, instance, **kwargs):
    try:
        student = Student.objects.get(profile__user=instance)
        student.extra_fields['last_logged_in'] = str(instance.last_login) if instance.last_login else None
        student.extra_fields['is_active'] = instance.is_active
        student.extra_fields['date_joined'] = instance.date_joined.strftime('%Y-%m-%d %H:%M:%S') if instance.date_joined else None
        student.extra_fields['full_name'] = f"{instance.first_name} {instance.last_name}".strip()
        student.save()
    except Student.DoesNotExist:
        pass

@receiver(post_save, sender=Profile)
def update_student_on_profile_save(sender, instance, **kwargs):
    try:
        student = Student.objects.get(profile=instance)
        student.extra_fields['is_verified'] = instance.is_email_verified and instance.is_phone_verified or instance.is_profile_complete
        student.extra_fields['age'] = instance.extra_fields.get('age', None)
        student.save()
    except Student.DoesNotExist:
        pass

@receiver(post_save, sender=Student)
def update_student_streak_on_save(sender, instance, **kwargs):
    if instance.streak_started_date:
        today = datetime.date.today()
        delta = today - instance.streak_started_date
        instance.extra_fields['streak_days'] = delta.days
        # Only save if streak_days has changed to avoid infinite loops
        # if instance.has_changed('extra_fields'):
        #     instance.save()
