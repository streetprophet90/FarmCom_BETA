from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # Event views
    path('', views.EventListView.as_view(), name='event_list'),
    path('event/<slug:slug>/', views.EventDetailView.as_view(), name='event_detail'),
    path('event/new/', views.EventCreateView.as_view(), name='event_create'),
    path('event/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_update'),
    path('event/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    
    # Category views
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # User interaction views
    path('event/<int:event_id>/like/', views.like_event, name='like_event'),
    path('event/<int:event_id>/register/', views.register_event, name='register_event'),
    path('event/<int:event_id>/unregister/', views.unregister_event, name='unregister_event'),
    path('event/<int:event_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
    
    # User-specific views
    path('my-events/', views.my_events, name='my_events'),
    path('my-registrations/', views.my_registrations, name='my_registrations'),
    
    # Search and calendar
    path('search/', views.search_events, name='search_events'),
    path('calendar/', views.event_calendar, name='event_calendar'),
] 