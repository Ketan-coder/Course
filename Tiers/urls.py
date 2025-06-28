from django.urls import path
from . import views

urlpatterns = [
    # path('', views.tier_list, name='tier_list'),
    # path('new/', views.tier_create, name='tier_new'),
    # path('edit/<int:pk>/', views.tier_update, name='tier_edit'),
    # path('delete/<int:pk>/', views.tier_delete, name='tier_delete'),

    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('tournament/<int:pk>/', views.tournament_detail_view, name='tournament_detail'),
    path('tiers/', views.tiers_view, name='tiers'),
]
