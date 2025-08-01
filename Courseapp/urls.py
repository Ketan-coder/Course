from django.urls import path
from django.urls.resolvers import URLPattern
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns: list[URLPattern] = [
    # path("", views.index, name="home"),
    path('courses/', views.course_list, name='course_list'),
    path("course/<int:pk>/", views.course_detail, name="course_detail"),
    path('courses/new/', login_required(views.course_create), name='course_create'),

    path('courses/step_one/', login_required(views.course_create_step_one), name='course_create_step_one'),
    path('courses/step_one/<int:course_id>/', login_required(views.course_create_step_one), name='course_create_step_one'),
    path('courses/step_two/', login_required(views.course_create_step_two), name='course_create_step_two'),
    path('courses/step_two/<int:course_id>/', login_required(views.course_create_step_two), name='course_create_step_two'),
    path('courses/step_three/', login_required(views.course_create_step_three), name='course_create_step_three'),
    path('courses/step_three/<int:course_id>/', login_required(views.course_create_step_three), name='course_create_step_three'),
    path('courses/step_four/', login_required(views.course_create_step_four), name='course_create_step_four'),
    path('courses/step_four/<int:course_id>/', login_required(views.course_create_step_four), name='course_create_step_four'),
    path('courses/step_five/', login_required(views.course_create_step_five), name='course_create_step_five'),
    path('courses/step_five/<int:course_id>/', login_required(views.course_create_step_five), name='course_create_step_five'),

    path('courses/bookmarked/', login_required(views.bookmarked_courses), name='bookmarked_courses'),
    path('courses/<int:pk>/edit/', login_required(views.course_update), name='course_update'),
    path('courses/<int:pk>/delete/', login_required(views.course_delete), name='course_delete'),

    path('courses/search_tags/', login_required(views.search_tags), name='search_tags'),
    path('courses/search_sections/', login_required(views.search_sections), name='search_sections'),
    path('courses/search_lesson/', login_required(views.search_lessons), name='search_lessons'),
    path('courses/search_faqs/', login_required(views.search_faqs), name='search_faqs'),
    path('courses/search_articles/', login_required(views.search_article), name='search_articles'),
    path("search-courses-htmx/", views.search_courses_htmx, name="search_courses_htmx"),


    path("detail/<int:lesson_id>/", login_required(views.video_detail_page), name="video_detail_page"),
    path("article/<int:article_id>/", login_required(views.article_detail), name="article_detail"),
    path("quizzes/<int:id>/questions/", login_required(views.get_quiz_questions), name="get_quiz_questions"),

    # urls.py
    path("mark/lesson/<int:lesson_id>/<int:user_profile>/complete/", login_required(views.mark_lesson_complete), name="mark_lesson_complete"),

    path("create_tag/", login_required(views.create_tag), name="create_tag"),
    path("create_section/", login_required(views.create_section), name="create_section"),
    path("create_lesson/", login_required(views.create_lesson), name="create_lesson"),
    path("create_faq/", login_required(views.create_faq), name="create_faq"),
    path("create_course_notes/", login_required(views.create_course_notes), name="create_course_notes"),
    path("create_article/", login_required(views.create_or_edit_article), name="create_article"),
    path("create_article/ajax/", login_required(views.create_article_ajax), name="create_article_ajax"),
    path("create_quiz/ajax/", login_required(views.create_quiz_ajax), name="create_quiz_ajax"),

    path("tags/edit/<int:tag_id>/", views.edit_tag, name="edit_tag"),

    path("quiz/new/", login_required(views.create_quiz), name="create_quiz"),
    path("quiz/submit/<int:quiz_id>/", login_required(views.submit_quiz), name="submit_quiz"),
    path('quiz/submit-dnd/<int:quiz_id>/', views.submit_drag_and_drop_quiz, name='submit_drag_and_drop_quiz'),
    path("course/bookmark/<int:course_id>/", login_required(views.bookmark_course), name="bookmark_course"),

    path('warmup/', views.quiz_warmup_start, name='quiz_warmup_start'),
    path('warmup/<int:quiz_id>/<int:qid>/', views.quiz_warmup_question, name='quiz_warmup_question'),

    path('lesson/add/', login_required(views.lesson_form), name='lesson_form'),
    path('lesson/<int:lesson_id>/', login_required(views.lesson_form), name='lesson_form'),

    path('fetch/lesson/<int:lesson_id>/', login_required(views.fetch_lesson_api), name='get_lesson_details'),

    path('fetch/section/<int:section_id>/', login_required(views.get_section_details), name='get_section_details'),
    path('fetch/quiz/<int:quiz_id>/', login_required(views.get_quiz_details), name='get_quiz_details'),
    path('fetch/article/<int:article_id>/', login_required(views.get_article_details), name='get_article_details'),
    # path('fetch/course/<int:course_id>/', login_required(views.fetch_course_api), name='fetch_course_api'),
    # path('fetch/course-notes/<int:course_id>/', login_required(views.fetch_course_notes_api), name='fetch_course_notes_api'),


    path('update-section-order/', login_required(views.update_section_order), name='update_section_order'),
    path('update-lesson-order/', login_required(views.update_lesson_order), name='update_lesson_order'),

    path('fetch-realtime-notes/<int:course_id>/', views.get_course_notes_htmx, name='fetch_realtime_notes'),
    path('fetch-realtime-notes/<int:course_id>/<int:section_id>/', views.get_course_notes_htmx, name='fetch_realtime_notes'),
    path('fetch-realtime-notes/<int:course_id>/<int:section_id>/<int:lesson_id>/', views.get_course_notes_htmx, name='fetch_realtime_notes'),

    # delete paths
    # path('delete_tag/<int:tag_id>/', login_required(views.delete_tag), name='delete_tag'),
    path('delete_section/<int:section_id>/', login_required(views.delete_section_api), name='delete_section'),
    path('delete_lesson/<int:lesson_id>/', login_required(views.delete_lesson_api), name='delete_lesson'),
    # path('delete_faq/<int:faq_id>/', login_required(views.delete_faq), name='delete_faq'),
    path('delete_article/<int:article_id>/', login_required(views.delete_article_api), name='delete_article'),
    path('delete_quiz/<int:quiz_id>/', login_required(views.delete_quiz_api), name='delete_quiz'),
    path('delete_article/<int:article_id>/', login_required(views.delete_article_api), name='delete_article'),
]
