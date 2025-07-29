from django.contrib import admin
from .models import Profile, Instructor, Student
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
            'fields': ('user', 'phone_no_prefix', 'phone_no', 'currency' , 'address', 'image', 'bio', 'date_of_birth', 'is_email_verified', 'is_phone_verified', 'is_profile_complete', 'isDarkTheme', 'theme')
        }),
        # Hidden fields for extra fields
        ('Extra Fields', {
            'fields': ('extra_fields',)
        }),
    )

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('profile', 'experience', 'rating', 'created_at')
    search_fields = ('profile__user__username', 'experience')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('profile', 'experience', 'rating')
        }),
        ('Extra Fields', {
            'fields': ('extra_fields',)
        }),
    )

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('profile', 'tier', 'rank', 'created_at')
    search_fields = ('profile__user__username', 'tier__name', 'rank__name')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('profile', 'tier', 'rank','score', 'daily_score')
        }),
        ('Extra Fields', {
            'fields': ('extra_fields',)
        }),
    )
