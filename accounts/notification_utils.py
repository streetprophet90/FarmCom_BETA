import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from .models import Notification, User


def get_notification_icon(notification_type):
    """Get appropriate icon for notification type"""
    icon_map = {
        'LAND_PENDING': 'fas fa-map-marker-alt',
        'PROJECT_PENDING': 'fas fa-project-diagram',
        'LAND_APPROVED': 'fas fa-check-circle',
        'LAND_REJECTED': 'fas fa-times-circle',
        'PROJECT_APPROVED': 'fas fa-check-circle',
        'PROJECT_REJECTED': 'fas fa-times-circle',
        'NEW_USER': 'fas fa-user-plus',
        'NEW_RECOMMENDATION': 'fas fa-lightbulb',
        'ACTIVITY_CONFIRMED': 'fas fa-check',
        'ACTIVITY_DISAPPROVED': 'fas fa-times',
        'NEW_ACTIVITY': 'fas fa-clipboard-list',
        'NEW_UPLOAD': 'fas fa-image',
        'PROJECT_UPDATE': 'fas fa-sync-alt',
        'TEAM_MESSAGE': 'fas fa-users',
        'TASK_ASSIGNED': 'fas fa-tasks',
        'TASK_COMPLETED': 'fas fa-flag-checkered',
        'WEATHER_ALERT': 'fas fa-cloud-rain',
        'EQUIPMENT_ISSUE': 'fas fa-tools',
        'MARKETPLACE_ORDER': 'fas fa-shopping-cart',
        'PAYMENT_RECEIVED': 'fas fa-money-bill-wave',
        'SYSTEM_MAINTENANCE': 'fas fa-cog',
        'TOPIC_REQUEST': 'fas fa-comment-dots',
        'TOPIC_REQUEST_APPROVED': 'fas fa-check-circle',
        'TOPIC_REQUEST_REJECTED': 'fas fa-times-circle',
        'TOPIC_REQUEST_UPDATED': 'fas fa-edit',
        'NEW_TOPIC': 'fas fa-plus-circle',
        'NEW_REPLY': 'fas fa-reply',
        'TOPIC_SUBSCRIPTION': 'fas fa-bell',
        'FORUM_MENTION': 'fas fa-at',
        'PERMISSION_GRANTED': 'fas fa-key',
        'PERMISSION_REVOKED': 'fas fa-lock',
        'PERMISSION_EXPIRED': 'fas fa-clock',
        'ADMIN_ACTION': 'fas fa-shield-alt',
        'PROFILE_UPDATE': 'fas fa-user-edit',
        'PASSWORD_CHANGE': 'fas fa-lock',
        'LOGIN_ALERT': 'fas fa-sign-in-alt',
        'SECURITY_ALERT': 'fas fa-exclamation-triangle',
        'BACKUP_COMPLETE': 'fas fa-database',
        'SYSTEM_UPDATE': 'fas fa-download',
    }
    return icon_map.get(notification_type, 'fas fa-bell')


def get_notification_color(notification_type):
    """Get appropriate color for notification type"""
    color_map = {
        'LAND_PENDING': 'warning',
        'PROJECT_PENDING': 'warning',
        'LAND_APPROVED': 'success',
        'LAND_REJECTED': 'danger',
        'PROJECT_APPROVED': 'success',
        'PROJECT_REJECTED': 'danger',
        'NEW_USER': 'info',
        'NEW_RECOMMENDATION': 'primary',
        'ACTIVITY_CONFIRMED': 'success',
        'ACTIVITY_DISAPPROVED': 'danger',
        'NEW_ACTIVITY': 'info',
        'NEW_UPLOAD': 'info',
        'PROJECT_UPDATE': 'primary',
        'TEAM_MESSAGE': 'primary',
        'TASK_ASSIGNED': 'warning',
        'TASK_COMPLETED': 'success',
        'WEATHER_ALERT': 'warning',
        'EQUIPMENT_ISSUE': 'danger',
        'MARKETPLACE_ORDER': 'success',
        'PAYMENT_RECEIVED': 'success',
        'SYSTEM_MAINTENANCE': 'secondary',
        'TOPIC_REQUEST': 'info',
        'TOPIC_REQUEST_APPROVED': 'success',
        'TOPIC_REQUEST_REJECTED': 'danger',
        'TOPIC_REQUEST_UPDATED': 'warning',
        'NEW_TOPIC': 'primary',
        'NEW_REPLY': 'info',
        'TOPIC_SUBSCRIPTION': 'info',
        'FORUM_MENTION': 'warning',
        'PERMISSION_GRANTED': 'success',
        'PERMISSION_REVOKED': 'danger',
        'PERMISSION_EXPIRED': 'warning',
        'ADMIN_ACTION': 'secondary',
        'PROFILE_UPDATE': 'info',
        'PASSWORD_CHANGE': 'warning',
        'LOGIN_ALERT': 'warning',
        'SECURITY_ALERT': 'danger',
        'BACKUP_COMPLETE': 'success',
        'SYSTEM_UPDATE': 'info',
    }
    return color_map.get(notification_type, 'primary')


def create_enhanced_notification(user, notification_type, title, message, related_object_id=None, related_object_type=None):
    """Enhanced notification creation with preferences check"""
    # Check user notification preferences
    if not user.email_notifications and not user.push_notifications:
        return None  # User has disabled all notifications
    
    # Create the notification
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        related_object_id=related_object_id,
        related_object_type=related_object_type
    )
    
    # Send email if enabled
    if user.email_notifications:
        from .views import send_email_notification
        send_email_notification(user, notification_type, title, message)
    
    # Send push notification if enabled
    if user.push_notifications:
        send_push_notification(user, notification)
    
    return notification


def send_push_notification(user, notification):
    """Send browser push notification"""
    # This would integrate with a service like Firebase Cloud Messaging
    # For now, we'll just log it
    print(f"Push notification sent to {user.username}: {notification.title}")


def get_recent_notifications_for_user(user, limit=10):
    """Get recent notifications with enhanced data"""
    notifications = Notification.objects.filter(user=user).order_by('-created_at')[:limit]
    
    enhanced_notifications = []
    for notification in notifications:
        enhanced_notifications.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'notification_type': notification.notification_type,
            'notification_type_display': notification.get_notification_type_display(),
            'is_read': notification.is_read,
            'created_at': notification.created_at,
            'created_at_ago': notification.created_at.strftime('%Y-%m-%d %H:%M'),
            'icon': get_notification_icon(notification.notification_type),
            'color': get_notification_color(notification.notification_type),
            'related_object_id': notification.related_object_id,
            'related_object_type': notification.related_object_type,
        })
    
    return enhanced_notifications


def get_notification_stats(user):
    """Get comprehensive notification statistics"""
    total_notifications = Notification.objects.filter(user=user).count()
    unread_notifications = Notification.objects.filter(user=user, is_read=False).count()
    read_notifications = total_notifications - unread_notifications
    
    # Notifications by type (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_notifications = Notification.objects.filter(
        user=user, 
        created_at__gte=thirty_days_ago
    )
    
    notifications_by_type = {}
    for notification in recent_notifications:
        notification_type = notification.notification_type
        if notification_type not in notifications_by_type:
            notifications_by_type[notification_type] = {
                'count': 0,
                'unread': 0,
                'display_name': notification.get_notification_type_display()
            }
        notifications_by_type[notification_type]['count'] += 1
        if not notification.is_read:
            notifications_by_type[notification_type]['unread'] += 1
    
    return {
        'total': total_notifications,
        'unread': unread_notifications,
        'read': read_notifications,
        'by_type': notifications_by_type,
    }


@login_required
@require_POST
def mark_notification_read_ajax(request, notification_id):
    """AJAX endpoint to mark notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
        
        # Get updated notification stats
        stats = get_notification_stats(request.user)
        
        return JsonResponse({
            'status': 'success',
            'notification_id': notification_id,
            'stats': stats
        })
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)


@login_required
@require_POST
def mark_all_notifications_read_ajax(request):
    """AJAX endpoint to mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    # Get updated notification stats
    stats = get_notification_stats(request.user)
    
    return JsonResponse({
        'status': 'success',
        'stats': stats
    })


@login_required
def get_notifications_ajax(request):
    """AJAX endpoint to get recent notifications"""
    limit = int(request.GET.get('limit', 10))
    notifications = get_recent_notifications_for_user(request.user, limit)
    
    return JsonResponse({
        'notifications': notifications,
        'unread_count': Notification.objects.filter(user=request.user, is_read=False).count()
    })


def create_bulk_notifications(users, notification_type, title, message, related_object_id=None, related_object_type=None):
    """Create notifications for multiple users"""
    notifications = []
    for user in users:
        if user.email_notifications or user.push_notifications:
            notification = create_enhanced_notification(
                user, notification_type, title, message, 
                related_object_id, related_object_type
            )
            if notification:
                notifications.append(notification)
    return notifications


def create_system_notification(notification_type, title, message, related_object_id=None, related_object_type=None):
    """Create system-wide notification for all users"""
    users = User.objects.filter(is_active=True)
    return create_bulk_notifications(users, notification_type, title, message, related_object_id, related_object_type) 