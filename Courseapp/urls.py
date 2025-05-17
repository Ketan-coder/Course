from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("course/<int:pk>/", views.course_detail, name="course_detail"),
]
