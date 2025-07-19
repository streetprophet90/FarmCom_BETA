from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import PermissionCategory, UserPermission, PermissionLog

@admin.register(PermissionCategory)
class PermissionCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']

@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'permission_type', 'permission_name', 'status', 
        'granted_by', 'granted_at', 'expires_at', 'usage_count'
    ]
    list_filter = [
        'permission_type', 'status', 'granted_at', 'expires_at',
        'can_create', 'can_update', 'can_delete', 'can_approve', 'can_reject'
    ]
    search_fields = ['user__username', 'user__email', 'permission_name', 'description']
    list_editable = ['status']
    readonly_fields = ['granted_at', 'last_used', 'usage_count']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'granted_by', 'permission_type', 'permission_name')
        }),
        ('Permission Details', {
            'fields': ('description', 'category', 'scope')
        }),
        ('Permissions', {
            'fields': ('can_create', 'can_read', 'can_update', 'can_delete', 'can_approve', 'can_reject')
        }),
        ('Time Settings', {
            'fields': ('status', 'expires_at')
        }),
        ('Usage Statistics', {
            'fields': ('granted_at', 'last_used', 'usage_count'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_permissions', 'deactivate_permissions', 'extend_expiry']
    
    def activate_permissions(self, request, queryset):
        updated = queryset.update(status='ACTIVE')
        self.message_user(request, f'{updated} permission(s) were successfully activated.')
    activate_permissions.short_description = "Activate selected permissions"
    
    def deactivate_permissions(self, request, queryset):
        updated = queryset.update(status='INACTIVE')
        self.message_user(request, f'{updated} permission(s) were successfully deactivated.')
    deactivate_permissions.short_description = "Deactivate selected permissions"
    
    def extend_expiry(self, request, queryset):
        # Extend expiry by 30 days
        new_expiry = timezone.now() + timezone.timedelta(days=30)
        updated = queryset.update(expires_at=new_expiry)
        self.message_user(request, f'{updated} permission(s) expiry was extended by 30 days.')
    extend_expiry.short_description = "Extend expiry by 30 days"
    
    def save_model(self, request, obj, form, change):
        if not change:  # New permission
            obj.granted_by = request.user
        super().save_model(request, obj, form, change)
        
        # Log the action
        action = 'MODIFIED' if change else 'GRANTED'
        PermissionLog.objects.create(
            permission=obj,
            action=action,
            performed_by=request.user,
            details=f"Permission {action.lower()} via admin interface",
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

@admin.register(PermissionLog)
class PermissionLogAdmin(admin.ModelAdmin):
    list_display = [
        'permission', 'action', 'performed_by', 'timestamp', 'ip_address'
    ]
    list_filter = ['action', 'timestamp', 'performed_by']
    search_fields = [
        'permission__user__username', 'permission__permission_name',
        'performed_by__username', 'details'
    ]
    readonly_fields = ['permission', 'action', 'performed_by', 'timestamp', 'ip_address', 'user_agent']
    
    def has_add_permission(self, request):
        return False  # Logs are created automatically
    
    def has_change_permission(self, request, obj=None):
        return False  # Logs should not be modified
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Only superusers can delete logs
