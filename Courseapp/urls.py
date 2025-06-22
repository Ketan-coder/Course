from django.urls import path
from django.urls.resolvers import URLPattern
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns: list[URLPattern] = [
    # path("", views.index, name="home"),
    path('courses/', views.course_list, name='course_list'),
    path("course/<int:pk>/", views.course_detail, name="course_detail"),
    path('courses/new/', login_required(views.course_create), name='course_create'),

    path('courses/bookmarked/', login_required(views.bookmarked_courses), name='bookmarked_courses'),
    path('courses/<int:pk>/edit/', login_required(views.course_update), name='course_update'),
    path('courses/<int:pk>/delete/', login_required(views.course_delete), name='course_delete'),

    path('courses/search_tags/', login_required(views.search_tags), name='search_tags'),
    path('courses/search_sections/', login_required(views.search_sections), name='search_sections'),
    path('courses/search_lesson/', login_required(views.search_lessons), name='search_lessons'),
    path('courses/search_faqs/', login_required(views.search_faqs), name='search_faqs'),

    path("detail/<int:lesson_id>/", login_required(views.video_detail_page), name="video_detail_page"),

    # urls.py
    path("lesson/<int:lesson_id>/<int:user_profile>/complete/", login_required(views.mark_lesson_complete), name="mark_lesson_complete"),

    path("create_tag/", login_required(views.create_tag), name="create_tag"),
    path("create_section/", login_required(views.create_section), name="create_section"),
    path("create_lesson/", login_required(views.create_lesson), name="create_lesson"),
    path("create_faq/", login_required(views.create_faq), name="create_faq"),
    path("create_course_notes/", login_required(views.create_course_notes), name="create_course_notes"),

    path("quiz/new/", login_required(views.create_quiz), name="create_quiz"),
    path("quiz/submit/<int:quiz_id>/", login_required(views.submit_quiz), name="submit_quiz"),
    path("course/bookmark/<int:course_id>/", login_required(views.bookmark_course), name="bookmark_course"),

    path('warmup/', views.quiz_warmup_start, name='quiz_warmup_start'),
    path('warmup/<int:quiz_id>/<int:qid>/', views.quiz_warmup_question, name='quiz_warmup_question'),
]
