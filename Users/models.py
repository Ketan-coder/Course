import uuid
from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_no_prefix = models.CharField(max_length=5, blank=True, null=True)
    phone_no = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(default='default_profile_pic.jpg', upload_to='profile_pics')
    bio = models.TextField(default="Hello, I am learning Stock Trading")
    date_of_birth = models.DateField(blank=True, null=True)
    email_confirmation_token = models.UUIDField(unique=True, blank=True, null=True)
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
        self.extra_fields['whole_phone_no'] = self.phone_no_prefix + self.phone_no if self.phone_no_prefix and self.phone_no else None
        if self.date_of_birth:
            self.extra_fields['age'] = (self.user.date_joined - self.date_of_birth).days // 365
        else:
            self.extra_fields['age'] = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Profile"
