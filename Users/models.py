from datetime import datetime
import uuid
from django.contrib.auth.models import User
from django.db import models
from utils.models import Currency, PhoneNoPrefix
from Courseapp.models import Course
from Tiers.models import Tier, TierRank


# Create your models here.
class Profile(models.Model):
    """User Profile model to store additional user information.
    This model extends the User model to include fields like phone number, address, bio, etc."""

    THEMES = (
        ('modern', 'Modern'),
        ('elegant', 'Elegant'),
        ('default', 'Default'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # phone_no_prefix = models.CharField(max_length=5, blank=True, null=True)
    phone_no_prefix = models.ForeignKey(PhoneNoPrefix, on_delete=models.SET_NULL, null=True, blank=True)
    phone_no = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(default='default_profile_pic.jpg', upload_to='profile_pics')
    bio = models.TextField(default="Hello, I am learning Stock Trading")
    date_of_birth = models.DateField(blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_profile_complete = models.BooleanField(default=False)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    email_confirmation_token = models.UUIDField(unique=True, blank=True, null=True)
    isDarkTheme = models.BooleanField(default=True)  # True for dark mode, False for light mode
    theme = models.CharField(max_length=20, choices=THEMES, default='default')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    extra_fields = models.JSONField(
        blank=True, null=True, default=dict, 
    )  # For any extra fields you want to add

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.email_confirmation_token:
            self.email_confirmation_token = uuid.uuid4()  # Generate only if empty
        self.extra_fields['last_logged_in'] = str(self.user.last_login) if self.user.last_login else None
        self.extra_fields['is_active'] = self.user.is_active
        self.extra_fields['date_joined'] = self.user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if self.user.date_joined else None
        self.extra_fields['whole_phone_no'] = self.phone_no_prefix.phone_no_prefix + self.phone_no if self.phone_no_prefix and self.phone_no else None
        if self.date_of_birth:
            # Convert date_of_birth string to a date object (if needed)
            if isinstance(self.date_of_birth, str):
                dob = datetime.strptime(self.date_of_birth, "%Y-%m-%d").date()
            else:
                dob = self.date_of_birth

            # Ensure join_date is a date
            join_date = self.user.date_joined.date()

            age_in_days = (join_date - dob).days
            self.extra_fields['age'] = age_in_days // 365
        else:
            self.extra_fields['age'] = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Instructor(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    associated_courses = models.ManyToManyField(Course, related_name='instructors', blank=True)
    experience = models.PositiveIntegerField(default=0)
    is_classroom_instructor = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.extra_fields['last_logged_in'] = str(self.profile.user.last_login) if self.profile.user.last_login else None
        self.extra_fields['is_active'] = self.profile.user.is_active
        self.extra_fields['date_joined'] = self.profile.user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if self.profile.user.date_joined else None
        self.extra_fields['full_name'] = f"{self.profile.user.first_name} {self.profile.user.last_name}".strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Instructor: {self.profile.user.username}"


class Student(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    enrolled_courses = models.ManyToManyField(Course, related_name='students', blank=True)
    wallet = models.OneToOneField("Stock.Wallet", on_delete=models.CASCADE, related_name='student_wallet', blank=True, null=True)
    score = models.PositiveIntegerField(default=0)
    daily_score = models.PositiveIntegerField(default=0)
    last_score_update_date = models.DateTimeField(auto_now_add=True)
    tier = models.ForeignKey(Tier, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    rank = models.ForeignKey(TierRank, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    streak_started_date = models.DateField(blank=True, null=True)
    streak = models.PositiveIntegerField(default=0)
    streak_last_updated_date = models.DateTimeField(auto_now_add=True)
    streak_freezes = models.PositiveSmallIntegerField(default=3)
    is_subscribed = models.BooleanField(default=False)
    subscription_start_date = models.DateField(blank=True, null=True)
    subscription_end_date = models.DateField(blank=True, null=True)
    subscription_type = models.CharField(
        max_length=50,
        choices=[('free', 'Free'), ('premium', 'Premium (Ad Free)')],
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.extra_fields['last_logged_in'] = str(self.profile.user.last_login) if self.profile.user.last_login else None
        self.extra_fields['is_active'] = self.profile.user.is_active
        self.extra_fields['date_joined'] = self.profile.user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if self.profile.user.date_joined else None
        self.extra_fields['full_name'] = f"{self.profile.user.first_name} {self.profile.user.last_name}".strip()
        self.extra_fields['is_verified'] = self.profile.is_email_verified and self.profile.is_phone_verified or self.profile.is_profile_complete
        self.extra_fields['is_active'] = self.profile.user.is_active
        self.extra_fields['age'] = self.profile.extra_fields.get('age', None)
        # calculate streak days with respect to todays date
        if self.streak_started_date:
            today = datetime.date.today()
            delta = today - self.streak_started_date
            self.extra_fields['streak_days'] = delta.days
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Student: {self.profile.user.username}"
    
    def get_full_name(self):
        """Return the full name of the student."""
        return f"{self.profile.user.first_name} {self.profile.user.last_name}".strip()
    
    def update_tier_and_rank(self):
        """Logic to determine the user's tier and rank based on their score."""
        tier = Tier.objects.filter(min_score__lte=self.score).order_by('-min_score').first()
        self.tier = tier
        if tier:
            # Logic to determine the rank within the tier (you might need more criteria)
            # For example, you could have score ranges within each tier for ranks.
            # This is a simplified example:
            ranks_in_tier = TierRank.objects.filter(tier=tier).order_by('order')
            if ranks_in_tier.exists():
                self.rank = ranks_in_tier.first() # Assign the lowest rank in the tier initially
                # You'll likely need more sophisticated logic here based on score or other factors
            else:
                self.rank = None
        else:
            self.rank = None
        self.save()
