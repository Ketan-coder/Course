from django.contrib import admin
from .models import Course, Section, Lesson, Quiz, QuizSubmission, Language, Tag

# Register your models here.

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'created_at')
    search_fields = ('name', 'symbol')
    ordering = ('name',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('name', 'symbol')
        }),
        ('Extra Fields', {
            'fields': ('extra_fields',)
        }),
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_code', 'created_at')
    search_fields = ('title', 'course_code')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('title', 'course_code', 'description', 'course_type', 'course_level', 'language', 'instructor', 'price', 'discount_price')
        }),
        ('Extra Fields', {
            'fields': ('extra_fields',)
        }),
    )


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'created_at')
    search_fields = ('title',)
    list_filter = ('created_at',)
    ordering = ('order',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('title', 'order', 'is_open')
        }),
        ('Extra Fields', {
            'fields': ('extra_fields',)
        }),
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'created_at')
    search_fields = ('course__title', 'title')
    list_filter = ('course__created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('course', 'section', 'title', 'description', 'video', 'content', 'is_open')
        }),
        ('Extra Fields', {
            'fields': ('extra_fields',)
        }),
    )


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'created_at')
    search_fields = ('course__title', 'title')
    list_filter = ('course__created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('course', 'section', 'lesson', 'title', 'description')
        }),
        ('Extra Fields', {
            'fields': ('extra_fields',)
        }),
    )


@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'get_quiz_questions', 'submitted_at')
    search_fields = ('quiz__title',)
    ordering = ('-submitted_at',)
    date_hierarchy = 'submitted_at'

    fieldsets = (
        (None, {
            'fields': ('quiz', 'quiz_questions')
        }),
        ('Extra Fields', {
            'fields': ('extra_fields',)
        }),
    )

    def get_quiz_questions(self, obj):
        # Assuming questions is a list of dicts in JSONField
        questions = obj.quiz.questions  # quiz.questions is a JSONField
        if isinstance(questions, list):
            return ", ".join([q.get("text", "") for q in questions])
        return "-"
    get_quiz_questions.short_description = 'Quiz Questions'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Extra Fields', {
            'fields': ('extra_fields',)
        }),
    )