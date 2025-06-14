from django.urls import path
from django.urls.resolvers import URLPattern
from . import views

urlpatterns: list[URLPattern] = [
    # path("", views.index, name="home"),
    path('courses/', views.course_list, name='course_list'),
    path("course/<int:pk>/", views.course_detail, name="course_detail"),
    path('courses/new/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_update, name='course_update'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),


    path('courses/search_tags/', views.search_tags, name='search_tags'),
    path('courses/search_sections/', views.search_sections, name='search_sections'),
    path('courses/search_lesson/', views.search_lessons, name='search_lessons'),
    path('courses/search_faqs/', views.search_faqs, name='search_faqs'),

    path("detail/<int:lesson_id>/", views.video_detail_page, name="video_detail_page"),

    # urls.py
    path("lesson/<int:lesson_id>/<int:user_profile>/complete/", views.mark_lesson_complete, name="mark_lesson_complete"),

    path("create_tag/", views.create_tag, name="create_tag"),
    path("create_section/", views.create_section, name="create_section"),
    path("create_lesson/", views.create_lesson, name="create_lesson"),
    path("create_faq/", views.create_faq, name="create_faq"),
]
