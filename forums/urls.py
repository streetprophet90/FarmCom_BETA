from django.urls import path
from . import views

app_name = 'forums'

urlpatterns = [
    # Category and topic listing
    path('', views.category_list, name='category_list'),
    path('topics/', views.topic_list, name='topic_list'),
    path('category/<slug:category_slug>/', views.topic_list, name='category_topics'),
    
    # Topic management
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('topic/new/', views.create_topic, name='create_topic'),
    path('topic/new/<slug:category_slug>/', views.create_topic, name='create_topic_in_category'),
    path('topic/<int:topic_id>/edit/', views.edit_topic, name='edit_topic'),
    path('topic/<int:topic_id>/delete/', views.delete_topic, name='delete_topic'),
    
    # Post management
    path('topic/<int:topic_id>/post/', views.create_post, name='create_post'),
    
    # Interactive features
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('topic/<int:topic_id>/subscribe/', views.subscribe_topic, name='subscribe_topic'),
    path('post/<int:post_id>/mark-solution/', views.mark_solution, name='mark_solution'),
    
    # Search
    path('search/', views.search_topics, name='search_topics'),
    
    # Topic Requests
    path('request-topic/', views.request_topic, name='request_topic'),
    path('my-requests/', views.my_topic_requests, name='my_topic_requests'),
] 