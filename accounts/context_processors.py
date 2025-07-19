from .models import Notification
from .utils import get_user_dashboard_url, get_user_home_url

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

def dashboard_url(request):
    """
    Add user dashboard URL to template context.
    """
    if request.user.is_authenticated:
        return {
            'user_dashboard_url': get_user_dashboard_url(request.user),
            'user_home_url': get_user_home_url(request.user)
        }
    return {
        'user_dashboard_url': 'home',
        'user_home_url': 'home'
    } 