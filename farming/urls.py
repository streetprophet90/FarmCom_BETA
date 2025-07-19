from django.urls import path
from . import views
 
urlpatterns = [
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/start/', views.start_project, name='start_project'),
    path('projects/<int:pk>/update-status/', views.update_project_status, name='update_project_status'),
    # Add more URL patterns as needed
] 