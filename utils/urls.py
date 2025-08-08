from django.urls import path
from django.urls.resolvers import URLPattern
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns: list[URLPattern] = [
    path('quiz_helper/', views.quiz_helper, name='quiz_helper'),
    path('home/', login_required(views.index), name='home'),
    path('', views.landing_page, name='landing_page'),
    path('toggle-dark/', login_required(views.toggle_dark_mode), name='toggle_dark_mode'),
    path('toggle-theme/', login_required(views.toggle_theme), name='toggle_theme'),
     path(
        "activity-loader/",
        login_required(views.activity_loader),
        name="activity_loader",
    ),
    path("activity-page/", login_required(views.activity_page), name="activity_page"),
    path(
        "delete-activity-request/",
        login_required(views.delete_activity_request),
        name="delete_activity_request",
    ),

    path('upload-video/', views.upload_video, name='upload_video'),
    path('update-quiz-submission-status/', views.update_quiz_submission_status, name='update_quiz_submission_status'),
]
