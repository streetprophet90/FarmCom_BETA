from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import UserPermission, PermissionLog
from django.db import models

User = get_user_model()

def has_permission(user, permission_type, permission_name, action='read', scope=None):
    """
    Check if a user has a specific permission
    
    Args:
        user: The user to check
        permission_type: Type of permission (e.g., 'FORUM_MANAGEMENT')
        permission_name: Specific permission name
        action: Action to check ('create', 'read', 'update', 'delete', 'approve', 'reject')
        scope: Optional scope to check against
    
    Returns:
        bool: True if user has permission, False otherwise
    """
    if not user.is_authenticated:
        return False
    
    # Superusers have all permissions
    if user.is_superuser:
        return True
    
    # Check for granted permissions
    permissions = UserPermission.objects.filter(
        user=user,
        permission_type=permission_type,
        permission_name=permission_name,
        status='ACTIVE'
    )
    
    for permission in permissions:
        # Check if permission is expired
        if permission.expires_at and permission.expires_at < timezone.now():
            permission.status = 'EXPIRED'
            permission.save()
            continue
        
        # Check scope if specified
        if scope and permission.scope:
            if scope not in permission.scope:
                continue
        
        # Check if user has the specific action permission
        if permission.has_permission(action):
            # Log usage
            permission.use_permission()
            PermissionLog.objects.create(
                permission=permission,
                action='USED',
                performed_by=user,
                details=f"Permission used: {action} on {permission_type}/{permission_name}",
                ip_address=get_client_ip(),
                user_agent=get_user_agent()
            )
            return True
    
    return False

def grant_permission(user, permission_type, permission_name, granted_by, 
                    description="", scope="", expires_at=None, **permissions):
    """
    Grant a permission to a user
    
    Args:
        user: User to grant permission to
        permission_type: Type of permission
        permission_name: Specific permission name
        granted_by: User granting the permission
        description: Description of the permission
        scope: Scope of the permission
        expires_at: When the permission expires
        **permissions: Additional permission flags (can_create, can_update, etc.)
    
    Returns:
        UserPermission: The created permission object
    """
    permission, created = UserPermission.objects.get_or_create(
        user=user,
        permission_type=permission_type,
        permission_name=permission_name,
        defaults={
            'granted_by': granted_by,
            'description': description,
            'scope': scope,
            'expires_at': expires_at,
            **permissions
        }
    )
    
    if not created:
        # Update existing permission
        for key, value in permissions.items():
            setattr(permission, key, value)
        permission.description = description
        permission.scope = scope
        permission.expires_at = expires_at
        permission.save()
    
    # Log the action
    action = 'GRANTED' if created else 'MODIFIED'
    PermissionLog.objects.create(
        permission=permission,
        action=action,
        performed_by=granted_by,
        details=f"Permission {action.lower()}: {permission_type}/{permission_name}",
        ip_address=get_client_ip(),
        user_agent=get_user_agent()
    )
    
    return permission

def revoke_permission(user, permission_type, permission_name, revoked_by, reason=""):
    """
    Revoke a permission from a user
    
    Args:
        user: User to revoke permission from
        permission_type: Type of permission
        permission_name: Specific permission name
        revoked_by: User revoking the permission
        reason: Reason for revocation
    
    Returns:
        bool: True if permission was revoked, False if not found
    """
    try:
        permission = UserPermission.objects.get(
            user=user,
            permission_type=permission_type,
            permission_name=permission_name
        )
        
        permission.status = 'INACTIVE'
        permission.save()
        
        # Log the action
        PermissionLog.objects.create(
            permission=permission,
            action='REVOKED',
            performed_by=revoked_by,
            details=f"Permission revoked: {reason}",
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )
        
        return True
    except UserPermission.DoesNotExist:
        return False

def get_user_permissions(user):
    """
    Get all active permissions for a user
    
    Args:
        user: User to get permissions for
    
    Returns:
        QuerySet: Active permissions for the user
    """
    if user.is_superuser:
        return UserPermission.objects.filter(status='ACTIVE')
    
    return UserPermission.objects.filter(
        user=user,
        status='ACTIVE'
    ).exclude(
        expires_at__lt=timezone.now()
    )

def get_permission_usage_stats(user=None, permission_type=None, days=30):
    """
    Get permission usage statistics
    
    Args:
        user: Optional user to filter by
        permission_type: Optional permission type to filter by
        days: Number of days to look back
    
    Returns:
        dict: Usage statistics
    """
    from datetime import timedelta
    
    start_date = timezone.now() - timedelta(days=days)
    
    logs = PermissionLog.objects.filter(timestamp__gte=start_date)
    
    if user:
        logs = logs.filter(permission__user=user)
    
    if permission_type:
        logs = logs.filter(permission__permission_type=permission_type)
    
    stats = {
        'total_uses': logs.filter(action='USED').count(),
        'permissions_granted': logs.filter(action='GRANTED').count(),
        'permissions_revoked': logs.filter(action='REVOKED').count(),
        'most_used_permissions': logs.filter(action='USED').values(
            'permission__permission_name'
        ).annotate(
            count=models.Count('id')
        ).order_by('-count')[:10]
    }
    
    return stats

# Helper functions for getting request information
def get_client_ip():
    """Get client IP address from request context"""
    # This would need to be called from within a view context
    # For now, return None
    return None

def get_user_agent():
    """Get user agent from request context"""
    # This would need to be called from within a view context
    # For now, return None
    return None

# Decorator for checking permissions
def require_permission(permission_type, permission_name, action='read', scope=None):
    """
    Decorator to require a specific permission for a view
    
    Usage:
        @require_permission('FORUM_MANAGEMENT', 'create_topics', 'create')
        def create_topic(request):
            # View code here
    """
    from django.shortcuts import redirect
    from django.contrib import messages
    from functools import wraps
    
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not has_permission(request.user, permission_type, permission_name, action, scope):
                messages.error(request, f'You do not have permission to {action} {permission_name}.')
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator 