from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class PermissionCategory(models.Model):
    """Categories of permissions that can be granted"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Permission Categories"
    
    def __str__(self):
        return self.name

class UserPermission(models.Model):
    """Specific permissions granted to users by superusers"""
    PERMISSION_TYPES = (
        ('FORUM_MANAGEMENT', 'Forum Management'),
        ('USER_MANAGEMENT', 'User Management'),
        ('LAND_APPROVAL', 'Land Approval'),
        ('PROJECT_APPROVAL', 'Project Approval'),
        ('CONTENT_MODERATION', 'Content Moderation'),
        ('REPORT_MANAGEMENT', 'Report Management'),
        ('NOTIFICATION_MANAGEMENT', 'Notification Management'),
        ('ANALYTICS_ACCESS', 'Analytics Access'),
        ('CUSTOM', 'Custom Permission'),
    )
    
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('EXPIRED', 'Expired'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_permissions')
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permissions_granted')
    permission_type = models.CharField(max_length=50, choices=PERMISSION_TYPES)
    permission_name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(PermissionCategory, on_delete=models.CASCADE, null=True, blank=True)
    
    # Scope - what this permission applies to
    scope = models.CharField(max_length=200, blank=True, help_text="Specific scope of this permission (e.g., specific categories, user types)")
    
    # Time limits
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Additional settings
    can_create = models.BooleanField(default=False)
    can_read = models.BooleanField(default=True)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_approve = models.BooleanField(default=False)
    can_reject = models.BooleanField(default=False)
    
    # Audit fields
    last_used = models.DateTimeField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'permission_type', 'permission_name']
        verbose_name_plural = "User Permissions"
    
    def __str__(self):
        return f"{self.user.username} - {self.permission_name}"
    
    def is_active(self):
        """Check if permission is currently active"""
        if self.status != 'ACTIVE':
            return False
        if self.expires_at and self.expires_at < timezone.now():
            self.status = 'EXPIRED'
            self.save()
            return False
        return True
    
    def has_permission(self, action):
        """Check if user has specific action permission"""
        if not self.is_active():
            return False
        
        action_map = {
            'create': self.can_create,
            'read': self.can_read,
            'update': self.can_update,
            'delete': self.can_delete,
            'approve': self.can_approve,
            'reject': self.can_reject,
        }
        return action_map.get(action, False)
    
    def use_permission(self):
        """Mark permission as used"""
        self.last_used = timezone.now()
        self.usage_count += 1
        self.save()

class PermissionLog(models.Model):
    """Log of permission usage for audit purposes"""
    ACTION_TYPES = (
        ('GRANTED', 'Permission Granted'),
        ('REVOKED', 'Permission Revoked'),
        ('USED', 'Permission Used'),
        ('EXPIRED', 'Permission Expired'),
        ('MODIFIED', 'Permission Modified'),
    )
    
    permission = models.ForeignKey(UserPermission, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permission_actions')
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.permission.user.username} - {self.action} - {self.timestamp}"
