from django.urls import path
from . import views

app_name = 'farmcom'

urlpatterns = [
    # Community News Management (superuser only)
    path('community-news/', views.community_news_list, name='community_news_list'),
    path('community-news/create/', views.community_news_create, name='community_news_create'),
    path('community-news/<int:pk>/edit/', views.community_news_edit, name='community_news_edit'),
    path('community-news/<int:pk>/delete/', views.community_news_delete, name='community_news_delete'),
    path('community-news/<int:pk>/toggle-active/', views.community_news_toggle_active, name='community_news_toggle_active'),
] 