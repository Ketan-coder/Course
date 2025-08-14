from typing import Literal
from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from .models import Language, Course, Section, Lesson, Quiz, QuizSubmission, Tag
from .models import CourseComment, CourseSubComment, CourseReview, CourseCertificate, FAQ, Article
from .admin_forms import TagForm
# Register your models here.


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name", "symbol", "created_at")
    search_fields = ("name", "symbol")
    ordering: tuple[Literal['name']] = ("name",)
    date_hierarchy = "created_at"
    fieldsets = (
        (None, {"fields": ("name", "symbol")}),
        ("Extra Fields", {"fields": ("extra_fields",)}),
    )

    class Media:
        css = {
            'all': ('admin/css/toggle-switch.css',)
        }
        js = ('admin/js/toggle-switch.js',)


class SectionInline(admin.TabularInline):
    model = Section.courses.through  # For ManyToManyField
    extra = 1

    class Media:
        css = {
            'all': ('admin/css/toggle-switch.css',)
        }
        js = ('admin/js/toggle-switch.js',)


class FAQInline(admin.TabularInline):
    model = FAQ.courses.through
    extra = 1

    class Media:
        css = {
            'all': ('admin/css/toggle-switch.css',)
        }
        js = ('admin/js/toggle-switch.js',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "course_code", "created_at")
    search_fields = ("title", "course_code")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    fieldsets = (
        (
            "Basic Details",
            {
                "fields": (
                    "title",
                    "course_code",
                    "course_uuid",
                    "description",
                    "course_type",
                    "course_level",
                    "language",
                    "instructor",
                    "price",
                    "discount_price",
                    "qr_code",
                    "is_class_room_course",
                )
            },
        ),
        (
            "Content Details",
            {
                "fields": (
                    "is_open_to_all",
                    "is_published",
                    "prerequisites",
                    "circulam",
                    "tags",
                    "is_bought_by_users",
                    "bookmarked_by_users",
                )  # Added tags here for basic display
            },
        ),
        ('Learning Objectives', {'fields': ('learning_objectives',)}),
        ("Media", {"fields": ("thumbnail", "intro_video")}),
        ("Extra Fields", {"fields": ("extra_fields",)}),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
    inlines = [SectionInline, FAQInline]  # To manage related Sections and FAQs
    readonly_fields = ("course_uuid", "created_at", "updated_at")

    class Media:
        css = {
            'all': ('admin/css/toggle-switch.css',)
        }
        js = ('admin/js/toggle-switch.js',)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "created_at")
    search_fields = ("title",)
    list_filter = ("created_at",)
    ordering = ("order",)
    date_hierarchy = "created_at"

    class Media:
        css = {
            'all': ('admin/css/toggle-switch.css',)
        }
        js = ('admin/js/toggle-switch.js',)
        
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
    list_display = ( "title", "created_at")
    search_fields = ("title",)
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    class Media:
        css = {
            'all': ('admin/css/toggle-switch.css',)
        }
        js = ('admin/js/toggle-switch.js',)

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
    list_display = ("course", "section", "lesson", "title", "created_at")
    search_fields = ("course__title", "title")
    list_filter = ("course__created_at",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    class Media:
        css = {
            'all': ('admin/css/toggle-switch.css',)
        }
        js = ('admin/js/toggle-switch.js',)

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
    list_display = ("quiz", "get_quiz_questions", "submitted_at")
    search_fields = ("quiz__title",)
    ordering = ("-submitted_at",)
    date_hierarchy = "submitted_at"
    # fieldsets = (
    #     (None, {
    #         'fields': ('quiz', 'quiz_questions')
    #     }),
    #     ('Extra Fields', {
    #         'fields': ('extra_fields',)
    #     }),
    # )

    class Media:
        css = {
            'all': ('admin/css/toggle-switch.css',)
        }
        js = ('admin/js/toggle-switch.js',)

    def get_quiz_questions(self, obj):
        # Assuming questions is a list of dicts in JSONField
        questions = obj.quiz.questions  # quiz.questions is a JSONField
        if isinstance(questions, list):
            return ", ".join([q.get("text", "") for q in questions])
        return "-"

    get_quiz_questions.short_description = "Quiz Questions"


# @admin.register(Tag)
# class TagAdmin(admin.ModelAdmin):
#     list_display = ("name", "created_at")
#     search_fields = ("name",)
#     ordering = ("name",)
#     date_hierarchy = "created_at"
#     fieldsets = (
#         (None, {
#             'fields': ('name','description',)
#         }),
#         ('Media', {
#             'fields': ('icon_image','extra_fields["icon"]')
#         }),
#         ('Extra Fields', {
#             'fields': ('is_deleted','is_active','extra_fields',)
#         }),
#     )

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    form = TagForm
    list_display = ("name", "created_at")
    search_fields = ("name",)
    ordering = ("name",)
    date_hierarchy = "created_at"

    class Media:
        css = {
            'all': ('admin/css/toggle-switch.css',)
        }
        js = ('admin/js/toggle-switch.js',)

    fieldsets = (
        ("Basic Info", {"fields": ("name", "description")}),
        ("Media", {"fields": ("icon_image",)}),
        ("Status", {"fields": ("is_active", "is_deleted")}),
        ("Extra Fields", {
            "fields": ("emoji", "icon", "bgColor", "color", "iconColor", "extra_fields"),
            "classes": ("collapse",)
        }),
    )

@admin.register(CourseComment)
class CourseCommentAdmin(admin.ModelAdmin):
    list_display = ("course", "user", "comment_text", "created_at")
    search_fields = ("course__title", "user__username", "comment_text")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    class Media:
        css = {
            'all': ('admin/css/toggle-switch.css',)
        }
        js = ('admin/js/toggle-switch.js',)
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
    list_display = ("course_comment", "user", "comment_text", "created_at")
    search_fields = (
        "course_comment_text__comment_text",
        "user__username",
        "comment_text",
    )
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    class Media:
        css = {
            'all': ('admin/css/toggle-switch.css',)
        }
        js = ('admin/js/toggle-switch.js',)
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
    list_display = ("user", "rating", "review_text", "created_at")
    search_fields = ("profile__user__username", "review_text")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    class Media:
        css = {
            'all': ('admin/css/toggle-switch.css',)
        }
        js = ('admin/js/toggle-switch.js',)
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
    list_display = ("user", "course", "certificate_code", "issued_at")
    search_fields = ("user__username", "course__title", "certificate_code")
    list_filter = ("issued_at",)
    ordering = ("-issued_at",)
    date_hierarchy = "issued_at"

    class Media:
        css = {
            'all': ('admin/css/toggle-switch.css',)
        }
        js = ('admin/js/toggle-switch.js',)
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
    list_display = ("question", "created_at")
    search_fields = ("question", "answer")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    class Media:
        css = {
            'all': ('admin/css/toggle-switch.css',)
        }
        js = ('admin/js/toggle-switch.js',)
    # fieldsets = (
    #     (None, {
    #         'fields': ('course', 'question', 'answer')
    #     }),
    #     ('Extra Fields', {
    #         'fields': ('extra_fields',)
    #     }),
    # )
    # )

@admin.register(Article)
class CourseArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at")
    search_fields = ("title", "content", "author__username")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'author')
        }),
        ('Extra Fields', {
            'fields': ('extra_fields',)
        }),
    )

    class Media:
        css = {
            'all': ('admin/css/toggle-switch.css',)
        }
        js = ('admin/js/toggle-switch.js',)