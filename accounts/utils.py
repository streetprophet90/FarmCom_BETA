def get_user_dashboard_url(user):
    """
    Get the appropriate dashboard URL based on user role.
    Returns the URL name for the user's dashboard.
    """
    if user.is_superuser:
        return 'admin_dashboard'
    elif user.user_type == 'FARMER':
        return 'farmer_dashboard'
    elif user.user_type == 'WORKER':
        return 'worker_dashboard'
    elif user.user_type == 'INVESTOR':
        return 'investor_dashboard'
    elif user.user_type == 'STUDENT':
        return 'student_dashboard'
    elif user.user_type == 'LANDOWNER':
        return 'landowner_home'  # Landowners use landowner_home as their dashboard
    else:
        return 'user_dashboard'  # Default fallback

def get_user_home_url(user):
    """
    Get the appropriate home URL based on user role.
    Returns the URL name for the user's home page.
    """
    if user.is_superuser:
        return 'superuser_home'  # Superusers go to their custom home page
    elif user.user_type == 'FARMER':
        return 'farmer_home'
    elif user.user_type == 'WORKER':
        return 'worker_home'
    elif user.user_type == 'INVESTOR':
        return 'investor_home'
    elif user.user_type == 'STUDENT':
        return 'student_home'
    elif user.user_type == 'LANDOWNER':
        return 'landowner_home'
    else:
        return 'logged_in_home'  # Default fallback 