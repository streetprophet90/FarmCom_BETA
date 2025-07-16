from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('farmer-dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    path('worker-dashboard/', views.worker_dashboard, name='worker_dashboard'),
    path('investor-home/', views.investor_home, name='investor_home'),
    path('investor-dashboard/', views.investor_dashboard, name='investor_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('contact-support/', views.contact_support, name='contact_support'),
    path('custom-login/', views.custom_login, name='custom_login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('approve-land/<int:land_id>/', views.approve_land, name='approve_land'),
    path('reject-land/<int:land_id>/', views.reject_land, name='reject_land'),
    path('approve-project/<int:project_id>/', views.approve_project, name='approve_project'),
    path('reject-project/<int:project_id>/', views.reject_project, name='reject_project'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('delete-land/<int:land_id>/', views.delete_land, name='delete_land'),
    path('delete-project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('delete-listing/<int:listing_id>/', views.delete_listing, name='delete_listing'),
    path('delete-recommendation/<int:rec_id>/', views.delete_recommendation, name='delete_recommendation'),
    path('edit-land/<int:land_id>/', views.edit_land, name='edit_land'),
    path('edit-project/<int:project_id>/', views.edit_project, name='edit_project'),
    path('bulk-approve-lands/', views.bulk_approve_lands, name='bulk_approve_lands'),
    path('bulk-reject-lands/', views.bulk_reject_lands, name='bulk_reject_lands'),
    path('bulk-approve-projects/', views.bulk_approve_projects, name='bulk_approve_projects'),
    path('bulk-reject-projects/', views.bulk_reject_projects, name='bulk_reject_projects'),
    path('mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('mark-all-notifications-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    path('admin-analytics/', views.admin_analytics, name='admin_analytics'),
    path('generate-report/', views.generate_report, name='generate_report'),
    # Add more URL patterns as needed
] 