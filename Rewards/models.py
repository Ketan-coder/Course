from django.db import models
from django.conf import settings
import uuid

from Users.models import Instructor, Student

class Voucher(models.Model):
    VOUCHER_TYPE_CHOICES = [
        ('standard', 'Standard Voucher'),
        ('referral_reward', 'Referral Reward'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    voucher_type = models.CharField(
        max_length=20,
        choices=VOUCHER_TYPE_CHOICES,
        default='standard',
    )
    is_percentage_based = models.BooleanField(default=False)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.IntegerField()
    expiry_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    # Referral specific fields
    referrer = models.ForeignKey(
        Instructor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referred_users_rewards'
    )
    referred_user = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referral_rewards'
    )
    referral_code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Unique code used for referral tracking."
    )

    def __str__(self):
        return f"{self.get_voucher_type_display()}: {self.name} (Code: {self.code if self.code else 'N/A'})"

    def save(self, *args, **kwargs):
        if self.voucher_type == 'referral_reward' and not self.code:
            self.code = self.generate_referral_reward_code()
        elif self.voucher_type == 'standard' and not self.code:
            self.code = self.generate_standard_voucher_code()
        super().save(*args, **kwargs)

    def generate_standard_voucher_code(self):
        # You can implement your own logic for generating standard voucher codes
        return f"VOUCHER-{uuid.uuid4().hex[:8].upper()}"

    def generate_referral_reward_code(self):
        # Unique code specific to the referral reward
        return f"REF-REWARD-{uuid.uuid4().hex[:10].upper()}"

    class Meta:
        ordering = ['-created_at']

class VoucherUsage(models.Model):
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='usage')
    user = models.ForeignKey('Users.Profile', on_delete=models.CASCADE, related_name='used_vouchers')
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voucher', 'user') # Prevent a user from using the same voucher multiple times (if that's your requirement)

    def __str__(self):
        return f"Voucher '{self.voucher.code}' used by {self.user.username} at {self.used_at}"