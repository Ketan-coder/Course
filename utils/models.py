# Suggested code may be subject to a license. Learn more: ~LicenseLog:1418672254.
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

# Create your models here.
class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)  # e.g. USD
    name = models.CharField(max_length=50)              # US Dollar
    symbol = models.CharField(max_length=5, unique=True)  # $
    country = models.CharField(max_length=50)
    decimal_digits = models.PositiveSmallIntegerField(default=2)  # For formatting: 2 for most currencies
    exchange_rate_to_usd = models.DecimalField(max_digits=12, decimal_places=6, default=1.0)  # Optional
    is_active = models.BooleanField(default=True)  # In case some currencies are outdated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.name}"

class PhoneNoPrefix(models.Model):
    phone_no_prefix = models.CharField(max_length=10)  # +91, +1
    country_code = models.CharField(max_length=10, unique=True)  # ISO alpha-2 code e.g. IN, US
    country_name = models.CharField(max_length=50)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True, related_name='phone_prefixes')
    flag_emoji = models.CharField(max_length=5, blank=True, null=True)  # 🇮🇳
    is_active = models.BooleanField(default=True)  # For soft-deprecation
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.country_name} ({self.phone_no_prefix})"


class FeedBack(models.Model):
    FEEDBACK_TYPE_CHOICES = [
        ('Contact Us','Contact Us'),
        ('Feedback','Feedback')
    ]

    name = models.CharField(max_length=100)
    feedback_type = models.CharField(max_length=50, choices=FEEDBACK_TYPE_CHOICES)
    email = models.EmailField()
    message = models.TextField()
    feedback_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False) # To mark feedback as read

    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.email}"
