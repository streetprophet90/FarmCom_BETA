from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import UserPermission, PermissionCategory
from .utils import grant_permission, revoke_permission, get_user_permissions

User = get_user_model()

@login_required
def manage_permissions(request):
    """Manage user permissions - superusers only"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser privileges required.')
        return redirect('home')
    
    users = User.objects.filter(is_superuser=False).order_by('username')
    categories = PermissionCategory.objects.filter(is_active=True)
    
    # Get user permissions for display
    user_permissions = {}
    for user in users:
        user_permissions[user.id] = get_user_permissions(user)
    
    context = {
        'users': users,
        'categories': categories,
        'user_permissions': user_permissions,
    }
    return render(request, 'user_permissions/manage_permissions.html', context)

@login_required
def grant_user_permission(request, user_id):
    """Grant a permission to a user - AJAX endpoint"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    if request.method == 'POST':
        try:
            user = get_object_or_404(User, id=user_id)
            permission_type = request.POST.get('permission_type')
            permission_name = request.POST.get('permission_name')
            description = request.POST.get('description', '')
            scope = request.POST.get('scope', '')
            
            # Parse permissions
            permissions = {
                'can_create': request.POST.get('can_create') == 'on',
                'can_read': request.POST.get('can_read') == 'on',
                'can_update': request.POST.get('can_update') == 'on',
                'can_delete': request.POST.get('can_delete') == 'on',
                'can_approve': request.POST.get('can_approve') == 'on',
                'can_reject': request.POST.get('can_reject') == 'on',
            }
            
            # Set expiry (default 30 days)
            expires_at = None
            if request.POST.get('expires_at'):
                expires_at = timezone.now() + timedelta(days=int(request.POST.get('expires_at')))
            
            permission = grant_permission(
                user=user,
                permission_type=permission_type,
                permission_name=permission_name,
                granted_by=request.user,
                description=description,
                scope=scope,
                expires_at=expires_at,
                **permissions
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Permission granted to {user.username}',
                'permission_id': permission.id
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def revoke_user_permission(request, permission_id):
    """Revoke a permission from a user - AJAX endpoint"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    if request.method == 'POST':
        try:
            permission = get_object_or_404(UserPermission, id=permission_id)
            reason = request.POST.get('reason', 'Revoked by administrator')
            
            success = revoke_permission(
                user=permission.user,
                permission_type=permission.permission_type,
                permission_name=permission.permission_name,
                revoked_by=request.user,
                reason=reason
            )
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': f'Permission revoked from {permission.user.username}'
                })
            else:
                return JsonResponse({'success': False, 'error': 'Permission not found'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def user_permissions_list(request, user_id):
    """View all permissions for a specific user"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser privileges required.')
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id)
    permissions = get_user_permissions(user)
    
    context = {
        'target_user': user,
        'permissions': permissions,
    }
    return render(request, 'user_permissions/user_permissions_list.html', context)

@login_required
def permission_usage_stats(request):
    """View permission usage statistics"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser privileges required.')
        return redirect('home')
    
    from .utils import get_permission_usage_stats
    
    # Get stats for last 30 days
    stats = get_permission_usage_stats(days=30)
    
    # Get top users by permission usage
    from .models import PermissionLog
    from django.db.models import Count
    
    top_users = PermissionLog.objects.filter(
        action='USED',
        timestamp__gte=timezone.now() - timedelta(days=30)
    ).values(
        'permission__user__username'
    ).annotate(
        usage_count=Count('id')
    ).order_by('-usage_count')[:10]
    
    context = {
        'stats': stats,
        'top_users': top_users,
    }
    return render(request, 'user_permissions/permission_usage_stats.html', context)
