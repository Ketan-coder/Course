from django.urls import path
from django.urls.resolvers import URLPattern
from . import views

urlpatterns: list[URLPattern] = [
    path('quiz_helper/', views.quiz_helper, name='quiz_helper'),
    path('home/', views.index, name='home'),
    path('', views.landing_page, name='landing_page'),
]
