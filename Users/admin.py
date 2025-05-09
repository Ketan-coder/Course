from django.contrib import admin
from .models import Profile
# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_no_prefix', 'phone_no', 'address', 'image', 'bio', 'date_of_birth', 'created_at')
    search_fields = ('user__username', 'phone_no_prefix', 'phone_no')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('user', 'phone_no_prefix', 'phone_no', 'address', 'image', 'bio', 'date_of_birth')
        }),
        ('Extra Fields', {
            'fields': ('extra_fields',)
        }),
    )
