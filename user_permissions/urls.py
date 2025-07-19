from django.urls import path
from . import views

app_name = 'user_permissions'

urlpatterns = [
    path('manage/', views.manage_permissions, name='manage_permissions'),
    path('grant/<int:user_id>/', views.grant_user_permission, name='grant_user_permission'),
    path('revoke/<int:permission_id>/', views.revoke_user_permission, name='revoke_user_permission'),
    path('user/<int:user_id>/', views.user_permissions_list, name='user_permissions_list'),
    path('stats/', views.permission_usage_stats, name='permission_usage_stats'),
] 