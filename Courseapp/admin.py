from django.contrib import admin
from .models import *

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

class SectionInline(admin.TabularInline):
    model = Section.courses.through # For ManyToManyField
    extra = 1

class FAQInline(admin.TabularInline):
    model = FAQ.courses.through
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_code', 'created_at')
    search_fields = ('title', 'course_code')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Basic Details', {
            'fields': ('title', 'course_code', 'course_uuid', 'description', 'course_type', 'course_level', 'language', 'instructor', 'price', 'discount_price')
        }),
        ('Content Details', {
            'fields': ('is_open_to_all', 'is_published', 'prerequisites', 'circulam', 'tags') # Added tags here for basic display
        }),
        ('Media', {
            'fields': ('thumbnail', 'intro_video')
        }),
        ('Extra Fields', {
            'fields': ('extra_fields',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    inlines = [SectionInline, FAQInline] # To manage related Sections and FAQs
    readonly_fields = ('course_uuid', 'created_at', 'updated_at')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'created_at')
    search_fields = ('title',)
    list_filter = ('created_at',)
    ordering = ('order',)
    date_hierarchy = 'created_at'
    # fieldsets = (
    #     (None, {
    #         'fields': ('title', 'order', 'is_open')
    #     }),
    #     ('Extra Fields', {
    #         'fields': ('extra_fields',)
    #     }),
    # )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'created_at')
    search_fields = ('course__title', 'title')
    list_filter = ('course__created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    # fieldsets = (
    #     (None, {
    #         'fields': ('course', 'section', 'title', 'description', 'video', 'content', 'is_open')
    #     }),
    #     ('Extra Fields', {
    #         'fields': ('extra_fields',)
    #     }),
    # )


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'created_at')
    search_fields = ('course__title', 'title')
    list_filter = ('course__created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    # fieldsets = (
    #     (None, {
    #         'fields': ('course', 'section', 'lesson', 'title', 'description')
    #     }),
    #     ('Extra Fields', {
    #         'fields': ('extra_fields',)
    #     }),
    # )


@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'get_quiz_questions', 'submitted_at')
    search_fields = ('quiz__title',)
    ordering = ('-submitted_at',)
    date_hierarchy = 'submitted_at'
    # fieldsets = (
    #     (None, {
    #         'fields': ('quiz', 'quiz_questions')
    #     }),
    #     ('Extra Fields', {
    #         'fields': ('extra_fields',)
    #     }),
    # )

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
    # fieldsets = (
    #     (None, {
    #         'fields': ('name',)
    #     }),
    #     ('Extra Fields', {
    #         'fields': ('extra_fields',)
    #     }),
    # )

@admin.register(CourseComment)
class CourseCommentAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'comment_text', 'created_at')
    search_fields = ('course__title', 'user__username', 'comment_text')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    # fieldsets = (
    #     (None, {
    #         'fields': ('course', 'user', 'comment_text')
    #     }),
    #     ('Extra Fields', {
    #         'fields': ('extra_fields',)
    #     }),
    # )

@admin.register(CourseSubComment)
class CourseSubCommentAdmin(admin.ModelAdmin):
    list_display = ('course_comment', 'user', 'comment_text', 'created_at')
    search_fields = ('course_comment_text__comment_text', 'user__username', 'comment_text')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    # fieldsets = (
    #     (None, {
    #         'fields': ('course_comment_text', 'user', 'comment_text')
    #     }),
    #     ('Extra Fields', {
    #         'fields': ('extra_fields',)
    #     }),
    # )

@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'review_text', 'created_at')
    search_fields = ('profile__user__username', 'review_text')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    # fieldsets = (
    #     (None, {
    #         'fields': ('user', 'rating', 'review_text')
    #     }),
    #     ('Extra Fields', {
    #         'fields': ('extra_fields',)
    #     }),
    # )

@admin.register(CourseCertificate)
class CourseCertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'certificate_code', 'issued_at')
    search_fields = ('user__username', 'course__title', 'certificate_code')
    list_filter = ('issued_at',)
    ordering = ('-issued_at',)
    date_hierarchy = 'issued_at'
    # fieldsets = (
    #     (None, {
    #         'fields': ('user', 'course', 'certificate_code')
    #     }),
    #     ('Extra Fields', {
    #         'fields': ('extra_fields',)
    #     }),
    # )


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at')
    search_fields = ('question', 'answer')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    # fieldsets = (
    #     (None, {
    #         'fields': ('course', 'question', 'answer')
    #     }),
    #     ('Extra Fields', {
    #         'fields': ('extra_fields',)
    #     }),
    # )
