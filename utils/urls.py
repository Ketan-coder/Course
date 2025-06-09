from django.urls import path
from django.urls.resolvers import URLPattern
from . import views

urlpatterns: list[URLPattern] = [
    path('home/', views.index, name='home'),
    path('', views.landing_page, name='landing_page'),
]
