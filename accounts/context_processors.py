from .models import Notification

def notification_data(request):
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
        recent_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
        return {
            'unread_notifications': unread_notifications,
            'recent_notifications': recent_notifications,
        }
    return {
        'unread_notifications': 0,
        'recent_notifications': [],
    } 