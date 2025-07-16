from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import login
from .forms import UserRegistrationForm, UserProfileForm, ImageUploadForm, ActivityLogForm, RecommendationForm, ContactSupportForm
from .models import ActivityLog, ImageUpload, User, Recommendation
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Avg, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import datetime, timedelta
import json
from django.contrib.admin.views.decorators import staff_member_required
from lands.models import Land
from farming.models import FarmingProject
from marketplace.models import CropListing
from accounts.models import Recommendation, ActivityLog, Notification, AdminAuditLog
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login

def get_activity_analytics(user, days=30):
    """Generate activity analytics data for charts"""
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Get daily activity counts
    daily_activities = ActivityLog.objects.filter(
        user=user,
        timestamp__gte=start_date,
        timestamp__lte=end_date
    ).extra(
        select={'day': 'date(timestamp)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Get daily upload counts
    daily_uploads = ImageUpload.objects.filter(
        user=user,
        timestamp__gte=start_date,
        timestamp__lte=end_date
    ).extra(
        select={'day': 'date(timestamp)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Prepare data for charts
    dates = []
    activity_counts = []
    upload_counts = []
    
    current_date = start_date.date()
    while current_date <= end_date.date():
        dates.append(current_date.strftime('%b %d'))
        
        # Find activity count for this date
        activity_count = next(
            (item['count'] for item in daily_activities if item['day'] == current_date),
            0
        )
        activity_counts.append(activity_count)
        
        # Find upload count for this date
        upload_count = next(
            (item['count'] for item in daily_uploads if item['day'] == current_date),
            0
        )
        upload_counts.append(upload_count)
        
        current_date += timedelta(days=1)
    
    return {
        'dates': dates,
        'activity_counts': activity_counts,
        'upload_counts': upload_counts,
        'total_activities': sum(activity_counts),
        'total_uploads': sum(upload_counts),
    }

def get_dashboard_url(user):
    if user.is_superuser:
        return 'admin_dashboard'
    if user.user_type == 'FARMER':
        return 'farmer_dashboard'
    elif user.user_type == 'WORKER':
        return 'worker_dashboard'
    elif user.user_type == 'INVESTOR':
        return 'investor_home'
    elif user.user_type == 'STUDENT':
        return 'student_dashboard'
    else:
        return 'user_dashboard'

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create notification for all superusers about new registration
            superusers = User.objects.filter(is_superuser=True)
            for admin in superusers:
                create_notification(
                    user=admin,
                    notification_type='NEW_USER',
                    title=f'New User Registration: {user.get_full_name() or user.username}',
                    message=f'New {user.get_user_type_display()} registered: {user.get_full_name() or user.username} ({user.email})',
                    related_object_id=user.id,
                    related_object_type='User'
                )
            
            login(request, user)
            dashboard_type = user.get_user_type_display() if hasattr(user, 'get_user_type_display') else user.user_type
            messages.success(request, f'Welcome to FarmCom, {user.first_name}! You are now in the {dashboard_type} Dashboard.')
            return redirect(get_dashboard_url(user))
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def user_dashboard(request):
    user = request.user
    uploads = ImageUpload.objects.filter(user=user).order_by('-timestamp')
    activities = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:20]
    progress = {
        'uploads_count': uploads.count(),
        'activity_count': activities.count(),
    }
    
    # Generate activity analytics data
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Get daily activity counts for the last 30 days
    daily_activities = ActivityLog.objects.filter(
        user=user,
        timestamp__gte=start_date,
        timestamp__lte=end_date
    ).extra(
        select={'day': 'date(timestamp)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Get daily upload counts for the last 30 days
    daily_uploads = ImageUpload.objects.filter(
        user=user,
        timestamp__gte=start_date,
        timestamp__lte=end_date
    ).extra(
        select={'day': 'date(timestamp)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Prepare chart data
    dates = []
    activity_counts = []
    upload_counts = []
    
    current_date = start_date.date()
    while current_date <= end_date.date():
        dates.append(current_date.strftime('%b %d'))
        
        # Find activity count for this date
        activity_count = next(
            (item['count'] for item in daily_activities if item['day'] == current_date),
            0
        )
        activity_counts.append(activity_count)
        
        # Find upload count for this date
        upload_count = next(
            (item['count'] for item in daily_uploads if item['day'] == current_date),
            0
        )
        upload_counts.append(upload_count)
        
        current_date += timedelta(days=1)
    
    analytics_data = {
        'dates': json.dumps(dates),
        'activity_counts': json.dumps(activity_counts),
        'upload_counts': json.dumps(upload_counts),
    }
    
    img_form = ImageUploadForm()
    act_form = ActivityLogForm()
    if request.method == 'POST':
        if 'upload_image' in request.POST:
            img_form = ImageUploadForm(request.POST, request.FILES)
            if img_form.is_valid():
                image_upload = img_form.save(commit=False)
                image_upload.user = user
                image_upload.save()
                
                # Create notification for supervisor if user is a worker
                if user.user_type == 'WORKER' and user.supervisor:
                    create_notification(
                        user=user.supervisor,
                        notification_type='NEW_UPLOAD',
                        title=f'New Upload from {user.get_full_name() or user.username}',
                        message=f'Worker {user.get_full_name() or user.username} uploaded a new image: {image_upload.description or "No description"}',
                        related_object_id=image_upload.id,
                        related_object_type='ImageUpload'
                    )
                
                messages.success(request, 'Image uploaded successfully!')
                return redirect('user_dashboard')
        elif 'log_activity' in request.POST:
            act_form = ActivityLogForm(request.POST)
            if act_form.is_valid():
                activity = act_form.save(commit=False)
                activity.user = user
                activity.save()
                
                # Create notification for supervisor if user is a worker
                if user.user_type == 'WORKER' and user.supervisor:
                    create_notification(
                        user=user.supervisor,
                        notification_type='NEW_ACTIVITY',
                        title=f'New Activity from {user.get_full_name() or user.username}',
                        message=f'Worker {user.get_full_name() or user.username} logged activity: {activity.action}',
                        related_object_id=activity.id,
                        related_object_type='ActivityLog'
                    )
                
                messages.success(request, 'Activity logged successfully!')
                return redirect('user_dashboard')
    # Calculate project progress
    from farming.models import FarmingProject
    if user.is_superuser:
        user_projects = FarmingProject.objects.filter(Q(manager=user) | Q(workers=user)).distinct()
    else:
        user_projects = FarmingProject.objects.filter(Q(manager=user) | Q(workers=user), approval_status='APPROVED').distinct()
    
    project_progress = []
    for project in user_projects:
        # Calculate progress based on status and activities
        if project.status == 'COMPLETED':
            progress_percentage = 100
        elif project.status == 'HARVESTED':
            progress_percentage = 90
        elif project.status == 'ACTIVE':
            # Calculate based on time elapsed vs total duration
            if project.end_date:
                total_days = (project.end_date - project.start_date).days
                elapsed_days = (timezone.now().date() - project.start_date).days
                if total_days > 0:
                    progress_percentage = min(80, max(20, (elapsed_days / total_days) * 80))
                else:
                    progress_percentage = 50
            else:
                progress_percentage = 50
        elif project.status == 'PLANNING':
            progress_percentage = 10
        else:
            progress_percentage = 0
            
        project_progress.append({
            'project': project,
            'percentage': progress_percentage,
            'status': project.get_status_display(),
        })
    
    return render(request, 'accounts/user_dashboard.html', {
        'progress': progress,
        'uploads': uploads,
        'activities': activities,
        'img_form': img_form,
        'act_form': act_form,
        'analytics_data': analytics_data,
        'project_progress': project_progress,
        **get_notification_data(user),
    })

@login_required
def farmer_dashboard(request):
    user = request.user
    if user.user_type != 'FARMER':
        return redirect('user_dashboard')
    # Get all workers supervised by this farmer
    workers = User.objects.filter(supervisor=user)
    # Get all uploads and activities from these workers
    worker_uploads = ImageUpload.objects.filter(user__in=workers).order_by('-timestamp')
    worker_activities = ActivityLog.objects.filter(user__in=workers).order_by('-timestamp')
    # Aggregated stats
    stats = {
        'worker_count': workers.count(),
        'total_uploads': worker_uploads.count(),
        'total_activities': worker_activities.count(),
    }
    
    # Generate team activity analytics data
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Get daily activity counts for the team (last 30 days)
    daily_activities = ActivityLog.objects.filter(
        user__in=workers,
        timestamp__gte=start_date,
        timestamp__lte=end_date
    ).extra(
        select={'day': 'date(timestamp)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Get daily upload counts for the team (last 30 days)
    daily_uploads = ImageUpload.objects.filter(
        user__in=workers,
        timestamp__gte=start_date,
        timestamp__lte=end_date
    ).extra(
        select={'day': 'date(timestamp)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Prepare chart data
    dates = []
    activity_counts = []
    upload_counts = []
    
    current_date = start_date.date()
    while current_date <= end_date.date():
        dates.append(current_date.strftime('%b %d'))
        
        # Find activity count for this date
        activity_count = next(
            (item['count'] for item in daily_activities if item['day'] == current_date),
            0
        )
        activity_counts.append(activity_count)
        
        # Find upload count for this date
        upload_count = next(
            (item['count'] for item in daily_uploads if item['day'] == current_date),
            0
        )
        upload_counts.append(upload_count)
        
        current_date += timedelta(days=1)
    
    analytics_data = {
        'dates': json.dumps(dates),
        'activity_counts': json.dumps(activity_counts),
        'upload_counts': json.dumps(upload_counts),
    }
    img_form = ImageUploadForm()
    act_form = ActivityLogForm()
    if request.method == 'POST':
        if 'upload_image' in request.POST:
            img_form = ImageUploadForm(request.POST, request.FILES)
            if img_form.is_valid():
                image_upload = img_form.save(commit=False)
                image_upload.user = user
                image_upload.save()
                messages.success(request, 'Image uploaded successfully!')
                return redirect('farmer_dashboard')
        elif 'log_activity' in request.POST:
            act_form = ActivityLogForm(request.POST)
            if act_form.is_valid():
                activity = act_form.save(commit=False)
                activity.user = user
                activity.save()
                messages.success(request, 'Activity logged successfully!')
                return redirect('farmer_dashboard')
        elif 'confirm_activity_id' in request.POST:
            activity_id = request.POST.get('confirm_activity_id')
            try:
                activity = ActivityLog.objects.get(id=activity_id, user__in=workers)
                activity.confirmed = True
                activity.save()
                
                # Create notification for the worker
                create_notification(
                    user=activity.user,
                    notification_type='ACTIVITY_CONFIRMED',
                    title='Activity Confirmed',
                    message=f'Your activity "{activity.action}" has been confirmed by your supervisor.',
                    related_object_id=activity.id,
                    related_object_type='ActivityLog'
                )
                
                messages.success(request, 'Activity confirmed!')
            except ActivityLog.DoesNotExist:
                messages.error(request, 'Activity not found or not allowed to confirm.')
            return redirect('farmer_dashboard')
        elif 'disapprove_activity_id' in request.POST:
            activity_id = request.POST.get('disapprove_activity_id')
            try:
                activity = ActivityLog.objects.get(id=activity_id, user__in=workers)
                activity.confirmed = False
                activity.save()
                
                # Create notification for the worker
                create_notification(
                    user=activity.user,
                    notification_type='ACTIVITY_DISAPPROVED',
                    title='Activity Disapproved',
                    message=f'Your activity "{activity.action}" has been disapproved by your supervisor.',
                    related_object_id=activity.id,
                    related_object_type='ActivityLog'
                )
                
                messages.success(request, 'Activity disapproved!')
            except ActivityLog.DoesNotExist:
                messages.error(request, 'Activity not found or not allowed to disapprove.')
            return redirect('farmer_dashboard')
    # Calculate team project progress
    from farming.models import FarmingProject
    if user.is_superuser:
        team_projects = FarmingProject.objects.all()
    else:
        team_projects = FarmingProject.objects.filter(approval_status='APPROVED')
    
    team_project_progress = []
    for project in team_projects:
        # Calculate progress based on status and activities
        if project.status == 'COMPLETED':
            progress_percentage = 100
        elif project.status == 'HARVESTED':
            progress_percentage = 90
        elif project.status == 'ACTIVE':
            # Calculate based on time elapsed vs total duration
            if project.end_date:
                total_days = (project.end_date - project.start_date).days
                elapsed_days = (timezone.now().date() - project.start_date).days
                if total_days > 0:
                    progress_percentage = min(80, max(20, (elapsed_days / total_days) * 80))
                else:
                    progress_percentage = 50
            else:
                progress_percentage = 50
        elif project.status == 'PLANNING':
            progress_percentage = 10
        else:
            progress_percentage = 0
            
        team_project_progress.append({
            'project': project,
            'percentage': progress_percentage,
            'status': project.get_status_display(),
        })
    
    return render(request, 'accounts/farmer_dashboard.html', {
        'stats': stats,
        'workers': workers,
        'worker_uploads': worker_uploads,
        'worker_activities': worker_activities,
        'img_form': img_form,
        'act_form': act_form,
        'analytics_data': analytics_data,
        'team_project_progress': team_project_progress,
        **get_notification_data(user),
    })

@login_required
def worker_dashboard(request):
    user = request.user
    if user.user_type != 'WORKER':
        return redirect('user_dashboard')
    
    # Get projects where user is a worker
    from farming.models import FarmingProject
    if user.is_superuser:
        user_projects = FarmingProject.objects.filter(workers=user).distinct()
    else:
        user_projects = FarmingProject.objects.filter(workers=user, approval_status='APPROVED').distinct()
    
    # Calculate project progress
    project_progress = []
    for project in user_projects:
        if project.status == 'COMPLETED':
            progress_percentage = 100
        elif project.status == 'HARVESTED':
            progress_percentage = 90
        elif project.status == 'ACTIVE':
            if project.end_date:
                total_days = (project.end_date - project.start_date).days
                elapsed_days = (timezone.now().date() - project.start_date).days
                if total_days > 0:
                    progress_percentage = min(80, max(20, (elapsed_days / total_days) * 80))
                else:
                    progress_percentage = 50
            else:
                progress_percentage = 50
        elif project.status == 'PLANNING':
            progress_percentage = 10
        else:
            progress_percentage = 0
        project_progress.append({
            'project': project,
            'percentage': progress_percentage,
            'status': project.get_status_display(),
        })
    
    # Get supervisor/farmer information
    supervisor = user.supervisor if hasattr(user, 'supervisor') else None
    
    # Get recent activities for this worker
    recent_activities = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:10]
    
    # Get recent uploads for this worker
    recent_uploads = ImageUpload.objects.filter(user=user).order_by('-timestamp')[:5]
    
    # Calculate performance stats
    total_activities = ActivityLog.objects.filter(user=user).count()
    total_uploads = ImageUpload.objects.filter(user=user).count()
    activities_this_week = ActivityLog.objects.filter(
        user=user, 
        timestamp__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Get team members (other workers under same supervisor)
    team_members = []
    if supervisor:
        team_members = User.objects.filter(supervisor=supervisor, user_type='WORKER').exclude(id=user.id)[:5]
    
    # Handle activity logging form
    act_form = ActivityLogForm()
    if request.method == 'POST':
        if 'log_activity' in request.POST:
            act_form = ActivityLogForm(request.POST)
            if act_form.is_valid():
                activity = act_form.save(commit=False)
                activity.user = user
                activity.save()
                messages.success(request, 'Activity logged successfully!')
                return redirect('worker_dashboard')
    
    # Generate activity analytics for the last 7 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=7)
    daily_activities = ActivityLog.objects.filter(
        user=user,
        timestamp__gte=start_date,
        timestamp__lte=end_date
    ).extra(
        select={'day': 'date(timestamp)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Prepare chart data
    dates = []
    activity_counts = []
    current_date = start_date.date()
    while current_date <= end_date.date():
        dates.append(current_date.strftime('%b %d'))
        activity_count = next(
            (item['count'] for item in daily_activities if item['day'] == current_date),
            0
        )
        activity_counts.append(activity_count)
        current_date += timedelta(days=1)
    
    analytics_data = {
        'dates': json.dumps(dates),
        'activity_counts': json.dumps(activity_counts),
    }
    
    # Mock data for additional features (in a real app, these would come from models)
    today_tasks = [
        {"task": "Water the corn field", "project": "Corn Project", "priority": "High", "completed": False},
        {"task": "Check irrigation system", "project": "Wheat Project", "priority": "Medium", "completed": True},
        {"task": "Harvest tomatoes", "project": "Vegetable Project", "priority": "High", "completed": False},
    ]
    
    work_schedule = [
        {"day": "Monday", "tasks": ["Field maintenance", "Equipment check"]},
        {"day": "Tuesday", "tasks": ["Planting", "Fertilizing"]},
        {"day": "Wednesday", "tasks": ["Irrigation", "Pest control"]},
        {"day": "Thursday", "tasks": ["Harvesting", "Storage prep"]},
        {"day": "Friday", "tasks": ["Equipment maintenance", "Planning"]},
    ]
    
    team_messages = [
        {"from": supervisor.get_full_name() if supervisor else "Supervisor", "message": "Great work on the irrigation system!", "time": "2 hours ago"},
        {"from": "Team Lead", "message": "Meeting tomorrow at 8 AM", "time": "1 day ago"},
    ]
    
    weather_info = {
        "temperature": "24°C",
        "condition": "Sunny",
        "humidity": "65%",
        "forecast": "Good for outdoor work"
    }
    
    equipment_status = [
        {"item": "Tractor", "status": "Available", "condition": "Good"},
        {"item": "Irrigation Pump", "status": "In Use", "condition": "Good"},
        {"item": "Harvesting Tools", "status": "Available", "condition": "Needs Maintenance"},
    ]
    
    return render(request, 'accounts/worker_dashboard.html', {
        'project_progress': project_progress,
        'supervisor': supervisor,
        'recent_activities': recent_activities,
        'recent_uploads': recent_uploads,
        'total_activities': total_activities,
        'total_uploads': total_uploads,
        'activities_this_week': activities_this_week,
        'team_members': team_members,
        'act_form': act_form,
        'analytics_data': analytics_data,
        'today_tasks': today_tasks,
        'work_schedule': work_schedule,
        'team_messages': team_messages,
        'weather_info': weather_info,
        'equipment_status': equipment_status,
        **get_notification_data(user),
    })

@login_required
def investor_home(request):
    """Investor home page - landing page before dashboard"""
    user = request.user
    if user.user_type != 'INVESTOR':
        return redirect('user_dashboard')
    
    # Get overview stats for investors
    from farming.models import FarmingProject
    from marketplace.models import CropListing
    from lands.models import Land
    
    total_projects = FarmingProject.objects.filter(approval_status='APPROVED').count()
    active_projects = FarmingProject.objects.filter(approval_status='APPROVED', status='ACTIVE').count()
    total_lands = Land.objects.filter(approval_status='APPROVED').count()
    total_listings = CropListing.objects.count()
    
    # Get recent marketplace activity
    recent_listings = CropListing.objects.select_related('project__land').order_by('-listing_date')[:5]
    
    # Get top performing projects
    top_projects = FarmingProject.objects.filter(
        approval_status='APPROVED'
    ).select_related('land', 'manager').order_by('-estimated_yield')[:5]
    
    # Get recent user registrations (for investment opportunities)
    recent_users = User.objects.filter(
        user_type__in=['FARMER', 'LANDOWNER']
    ).order_by('-date_joined')[:5]
    
    return render(request, 'accounts/investor_home.html', {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_lands': total_lands,
        'total_listings': total_listings,
        'recent_listings': recent_listings,
        'top_projects': top_projects,
        'recent_users': recent_users,
        **get_notification_data(user),
    })

@login_required
def investor_dashboard(request):
    """Investor dashboard - detailed view"""
    user = request.user
    if user.user_type != 'INVESTOR':
        return redirect('user_dashboard')
    
    # Get projects the investor is observing (for now, show all projects)
    from farming.models import FarmingProject
    if user.is_superuser:
        user_projects = FarmingProject.objects.all()
    else:
        user_projects = FarmingProject.objects.filter(approval_status='APPROVED')
    
    project_progress = []
    for project in user_projects:
        if project.status == 'COMPLETED':
            progress_percentage = 100
        elif project.status == 'HARVESTED':
            progress_percentage = 90
        elif project.status == 'ACTIVE':
            if project.end_date:
                total_days = (project.end_date - project.start_date).days
                elapsed_days = (timezone.now().date() - project.start_date).days
                if total_days > 0:
                    progress_percentage = min(80, max(20, (elapsed_days / total_days) * 80))
                else:
                    progress_percentage = 50
            else:
                progress_percentage = 50
        elif project.status == 'PLANNING':
            progress_percentage = 10
        else:
            progress_percentage = 0
        project_progress.append({
            'project': project,
            'percentage': progress_percentage,
            'status': project.get_status_display(),
        })
    
    return render(request, 'accounts/investor_dashboard.html', {
        'project_progress': project_progress,
        **get_notification_data(user),
    })

@login_required
def student_dashboard(request):
    user = request.user
    if user.user_type != 'STUDENT':
        return redirect('user_dashboard')
    # Get all projects for learning purposes
    from farming.models import FarmingProject
    if user.is_superuser:
        user_projects = FarmingProject.objects.all()
    else:
        user_projects = FarmingProject.objects.filter(approval_status='APPROVED')
    project_progress = []
    for project in user_projects:
        if project.status == 'COMPLETED':
            progress_percentage = 100
        elif project.status == 'HARVESTED':
            progress_percentage = 90
        elif project.status == 'ACTIVE':
            if project.end_date:
                total_days = (project.end_date - project.start_date).days
                elapsed_days = (timezone.now().date() - project.start_date).days
                if total_days > 0:
                    progress_percentage = min(80, max(20, (elapsed_days / total_days) * 80))
                else:
                    progress_percentage = 50
            else:
                progress_percentage = 50
        elif project.status == 'PLANNING':
            progress_percentage = 10
        else:
            progress_percentage = 0
        project_progress.append({
            'project': project,
            'percentage': progress_percentage,
            'status': project.get_status_display(),
        })
    # Handle recommendation form
    form = RecommendationForm()
    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            rec = form.save(commit=False)
            rec.user = user
            rec.save()
            
            # Create notification for all superusers about new recommendation
            superusers = User.objects.filter(is_superuser=True)
            for admin in superusers:
                create_notification(
                    user=admin,
                    notification_type='NEW_RECOMMENDATION',
                    title=f'New Recommendation from {user.get_full_name() or user.username}',
                    message=f'Student {user.get_full_name() or user.username} submitted a new recommendation: {rec.content[:50]}...',
                    related_object_id=rec.id,
                    related_object_type='Recommendation'
                )
            
            messages.success(request, 'Recommendation submitted!')
            return redirect('student_dashboard')
    recommendations = Recommendation.objects.order_by('-timestamp')[:10]
    return render(request, 'accounts/student_dashboard.html', {
        'project_progress': project_progress,
        'form': form,
        'recommendations': recommendations,
        **get_notification_data(user),
    })

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')
    # Key stats
    user_counts = User.objects.values('user_type').order_by('user_type').annotate(count=Count('id'))
    total_users = User.objects.count()
    total_lands = Land.objects.count()
    total_projects = FarmingProject.objects.count()
    total_listings = CropListing.objects.count()
    total_recommendations = Recommendation.objects.count()
    total_activities = ActivityLog.objects.count()
    # Recent activity
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_lands = Land.objects.order_by('-date_listed')[:5]
    recent_projects = FarmingProject.objects.order_by('-start_date')[:5]
    recent_recommendations = Recommendation.objects.order_by('-timestamp')[:5]
    # Management tables
    user_list = User.objects.all().order_by('-date_joined')
    user_paginator = Paginator(user_list, 10)
    user_page = request.GET.get('user_page') or 1
    users_paginated = user_paginator.get_page(user_page)
    lands = Land.objects.all().order_by('-date_listed')
    projects = FarmingProject.objects.all().order_by('-start_date')
    listings = CropListing.objects.all().order_by('-id')
    recommendations = Recommendation.objects.all().order_by('-timestamp')
    # Separate pending lands and projects for quick access in template
    pending_lands = lands.filter(approval_status='PENDING')
    pending_projects = projects.filter(approval_status='PENDING')
    
    # Add notification data
    unread_notifications = Notification.objects.filter(is_read=False).count()
    recent_notifications = Notification.objects.filter(is_read=False).order_by('-created_at')[:5]
    
    # Add community news statistics
    from farmcom.models import CommunityNews
    total_news_items = CommunityNews.objects.count()
    active_news_items = CommunityNews.objects.filter(is_active=True).count()
    inactive_news_items = CommunityNews.objects.filter(is_active=False).count()
    
    return render(request, 'accounts/admin_dashboard.html', {
        'user_counts': user_counts,
        'total_users': total_users,
        'total_lands': total_lands,
        'total_projects': total_projects,
        'total_listings': total_listings,
        'total_recommendations': total_recommendations,
        'total_activities': total_activities,
        'recent_users': recent_users,
        'recent_lands': recent_lands,
        'recent_projects': recent_projects,
        'recent_recommendations': recent_recommendations,
        'users_paginated': users_paginated,
        'lands': lands,
        'projects': projects,
        'listings': listings,
        'recommendations': recommendations,
        'pending_lands': pending_lands,
        'pending_projects': pending_projects,
        'unread_notifications': unread_notifications,
        'recent_notifications': recent_notifications,
        'total_news_items': total_news_items,
        'active_news_items': active_news_items,
        'inactive_news_items': inactive_news_items,
    })

def superuser_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_superuser)(view_func)
    return decorated_view_func

def create_notification(user, notification_type, title, message, related_object_id=None, related_object_type=None):
    """Helper function to create notifications"""
    Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        related_object_id=related_object_id,
        related_object_type=related_object_type
    )

def get_notification_data(user):
    """Helper function to get notification data for any user"""
    unread_notifications = Notification.objects.filter(user=user, is_read=False).count()
    recent_notifications = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')[:5]
    return {
        'unread_notifications': unread_notifications,
        'recent_notifications': recent_notifications,
    }

def log_admin_action(request, action_type, target_object_type, target_object_id, target_object_name, details=""):
    """Helper function to log admin actions"""
    AdminAuditLog.objects.create(
        admin_user=request.user,
        action_type=action_type,
        target_object_type=target_object_type,
        target_object_id=target_object_id,
        target_object_name=target_object_name,
        details=details,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

@superuser_required
def approve_land(request, land_id):
    land = get_object_or_404(Land, id=land_id)
    land.approval_status = 'APPROVED'
    land.save()
    messages.success(request, f'Land "{land.title}" approved.')
    
    # Log audit action
    log_admin_action(request, 'APPROVE_LAND', 'Land', land.id, land.title)
    
    # Create notification for land owner
    create_notification(
        user=land.owner,
        notification_type='LAND_APPROVED',
        title=f'Land "{land.title}" Approved',
        message=f'Your land "{land.title}" has been approved and is now visible to other users.',
        related_object_id=land.id,
        related_object_type='Land'
    )
    
    return redirect(reverse('admin_dashboard'))

@superuser_required
def reject_land(request, land_id):
    land = get_object_or_404(Land, id=land_id)
    land.approval_status = 'REJECTED'
    land.save()
    messages.warning(request, f'Land "{land.title}" rejected.')
    
    # Log audit action
    log_admin_action(request, 'REJECT_LAND', 'Land', land.id, land.title)
    
    # Create notification for land owner
    create_notification(
        user=land.owner,
        notification_type='LAND_REJECTED',
        title=f'Land "{land.title}" Rejected',
        message=f'Your land "{land.title}" has been rejected. Please review and resubmit if needed.',
        related_object_id=land.id,
        related_object_type='Land'
    )
    
    return redirect(reverse('admin_dashboard'))

@superuser_required
def approve_project(request, project_id):
    project = get_object_or_404(FarmingProject, id=project_id)
    project.approval_status = 'APPROVED'
    project.save()
    messages.success(request, f'Project "{project}" approved.')
    
    # Log audit action
    log_admin_action(request, 'APPROVE_PROJECT', 'FarmingProject', project.id, str(project))
    
    # Create notification for project manager
    create_notification(
        user=project.manager,
        notification_type='PROJECT_APPROVED',
        title=f'Project "{project}" Approved',
        message=f'Your project "{project}" has been approved and is now active.',
        related_object_id=project.id,
        related_object_type='FarmingProject'
    )
    
    return redirect(reverse('admin_dashboard'))

@superuser_required
def reject_project(request, project_id):
    project = get_object_or_404(FarmingProject, id=project_id)
    project.approval_status = 'REJECTED'
    project.save()
    messages.warning(request, f'Project "{project}" rejected.')
    
    # Log audit action
    log_admin_action(request, 'REJECT_PROJECT', 'FarmingProject', project.id, str(project))
    
    # Create notification for project manager
    create_notification(
        user=project.manager,
        notification_type='PROJECT_REJECTED',
        title=f'Project "{project}" Rejected',
        message=f'Your project "{project}" has been rejected. Please review and resubmit if needed.',
        related_object_id=project.id,
        related_object_type='FarmingProject'
    )
    
    return redirect(reverse('admin_dashboard'))

@superuser_required
def bulk_approve_lands(request):
    if request.method == 'POST':
        land_ids = request.POST.getlist('land_ids')
        approved_count = 0
        approved_lands = []
        for land_id in land_ids:
            try:
                land = Land.objects.get(id=land_id, approval_status='PENDING')
                land.approval_status = 'APPROVED'
                land.save()
                approved_count += 1
                approved_lands.append(land.title)
            except Land.DoesNotExist:
                continue
        
        # Log bulk audit action
        if approved_count > 0:
            log_admin_action(request, 'BULK_APPROVE_LANDS', 'Land', 0, 
                           f"Bulk approved {approved_count} lands", 
                           f"Approved lands: {', '.join(approved_lands)}")
            messages.success(request, f'{approved_count} land(s) approved successfully.')
        else:
            messages.warning(request, 'No lands were approved.')
    return redirect(reverse('admin_dashboard'))

@superuser_required
def bulk_reject_lands(request):
    if request.method == 'POST':
        land_ids = request.POST.getlist('land_ids')
        rejected_count = 0
        rejected_lands = []
        for land_id in land_ids:
            try:
                land = Land.objects.get(id=land_id, approval_status='PENDING')
                land.approval_status = 'REJECTED'
                land.save()
                rejected_count += 1
                rejected_lands.append(land.title)
            except Land.DoesNotExist:
                continue
        
        # Log bulk audit action
        if rejected_count > 0:
            log_admin_action(request, 'BULK_REJECT_LANDS', 'Land', 0,
                           f"Bulk rejected {rejected_count} lands",
                           f"Rejected lands: {', '.join(rejected_lands)}")
            messages.warning(request, f'{rejected_count} land(s) rejected.')
        else:
            messages.warning(request, 'No lands were rejected.')
    return redirect(reverse('admin_dashboard'))

@superuser_required
def bulk_approve_projects(request):
    if request.method == 'POST':
        project_ids = request.POST.getlist('project_ids')
        approved_count = 0
        approved_projects = []
        for project_id in project_ids:
            try:
                project = FarmingProject.objects.get(id=project_id, approval_status='PENDING')
                project.approval_status = 'APPROVED'
                project.save()
                approved_count += 1
                approved_projects.append(str(project))
            except FarmingProject.DoesNotExist:
                continue
        
        # Log bulk audit action
        if approved_count > 0:
            log_admin_action(request, 'BULK_APPROVE_PROJECTS', 'FarmingProject', 0,
                           f"Bulk approved {approved_count} projects",
                           f"Approved projects: {', '.join(approved_projects)}")
            messages.success(request, f'{approved_count} project(s) approved successfully.')
        else:
            messages.warning(request, 'No projects were approved.')
    return redirect(reverse('admin_dashboard'))

@superuser_required
def bulk_reject_projects(request):
    if request.method == 'POST':
        project_ids = request.POST.getlist('project_ids')
        rejected_count = 0
        rejected_projects = []
        for project_id in project_ids:
            try:
                project = FarmingProject.objects.get(id=project_id, approval_status='PENDING')
                project.approval_status = 'REJECTED'
                project.save()
                rejected_count += 1
                rejected_projects.append(str(project))
            except FarmingProject.DoesNotExist:
                continue
        
        # Log bulk audit action
        if rejected_count > 0:
            log_admin_action(request, 'BULK_REJECT_PROJECTS', 'FarmingProject', 0,
                           f"Bulk rejected {rejected_count} projects",
                           f"Rejected projects: {', '.join(rejected_projects)}")
            messages.warning(request, f'{rejected_count} project(s) rejected.')
        else:
            messages.warning(request, 'No projects were rejected.')
    return redirect(reverse('admin_dashboard'))

@superuser_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect(reverse('admin_dashboard'))
    username = user.username
    user.delete()
    messages.success(request, f'User "{username}" deleted successfully.')
    
    # Log audit action
    log_admin_action(request, 'DELETE_USER', 'User', user_id, username)
    
    return redirect(reverse('admin_dashboard'))

@superuser_required
def delete_land(request, land_id):
    land = get_object_or_404(Land, id=land_id)
    title = land.title
    land.delete()
    messages.success(request, f'Land "{title}" deleted successfully.')
    
    # Log audit action
    log_admin_action(request, 'DELETE_LAND', 'Land', land_id, title)
    
    return redirect(reverse('admin_dashboard'))

@superuser_required
def delete_project(request, project_id):
    project = get_object_or_404(FarmingProject, id=project_id)
    project_name = str(project)
    project.delete()
    messages.success(request, f'Project "{project_name}" deleted successfully.')
    
    # Log audit action
    log_admin_action(request, 'DELETE_PROJECT', 'FarmingProject', project_id, project_name)
    
    return redirect(reverse('admin_dashboard'))

@superuser_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(CropListing, id=listing_id)
    listing_name = str(listing)
    listing.delete()
    messages.success(request, f'Listing "{listing_name}" deleted successfully.')
    
    # Log audit action
    log_admin_action(request, 'DELETE_LISTING', 'CropListing', listing_id, listing_name)
    
    return redirect(reverse('admin_dashboard'))

@superuser_required
def delete_recommendation(request, rec_id):
    recommendation = get_object_or_404(Recommendation, id=rec_id)
    rec_title = recommendation.title
    recommendation.delete()
    messages.success(request, f'Recommendation "{rec_title}" deleted successfully.')
    
    # Log audit action
    log_admin_action(request, 'DELETE_RECOMMENDATION', 'Recommendation', rec_id, rec_title)
    
    return redirect(reverse('admin_dashboard'))

@superuser_required
def edit_land(request, land_id):
    land = get_object_or_404(Land, id=land_id)
    if request.method == 'POST':
        # Log audit action before changes
        log_admin_action(request, 'EDIT_LAND', 'Land', land.id, land.title, 
                        f"Edited fields: {', '.join(request.POST.keys())}")
        
        # Handle form submission for editing land
        land.title = request.POST.get('title', land.title)
        land.location = request.POST.get('location', land.location)
        land.size = request.POST.get('size', land.size)
        land.description = request.POST.get('description', land.description)
        land.preferred_crops = request.POST.get('preferred_crops', land.preferred_crops)
        land.soil_type = request.POST.get('soil_type', land.soil_type)
        land.water_source = request.POST.get('water_source', land.water_source)
        land.is_available = request.POST.get('is_available') == 'on'
        land.save()
        messages.success(request, f'Land "{land.title}" updated successfully.')
        return redirect(reverse('admin_dashboard'))
    return render(request, 'accounts/edit_land.html', {'land': land})

@superuser_required
def edit_project(request, project_id):
    project = get_object_or_404(FarmingProject, id=project_id)
    if request.method == 'POST':
        # Log audit action before changes
        log_admin_action(request, 'EDIT_PROJECT', 'FarmingProject', project.id, str(project),
                        f"Edited fields: {', '.join(request.POST.keys())}")
        
        # Handle form submission for editing project
        project.crops = request.POST.get('crops', project.crops)
        project.status = request.POST.get('status', project.status)
        project.estimated_yield = request.POST.get('estimated_yield', project.estimated_yield)
        project.save()
        messages.success(request, f'Project "{project}" updated successfully.')
        return redirect(reverse('admin_dashboard'))
    return render(request, 'accounts/edit_project.html', {'project': project})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    return JsonResponse({'status': 'success'})

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

@superuser_required
def audit_logs(request):
    """View admin audit logs"""
    logs = AdminAuditLog.objects.all().order_by('-timestamp')
    paginator = Paginator(logs, 50)
    page = request.GET.get('page')
    logs_paginated = paginator.get_page(page)
    
    return render(request, 'accounts/audit_logs.html', {
        'logs': logs_paginated,
    })

@superuser_required
def admin_analytics(request):
    """Comprehensive analytics and reporting for admin dashboard"""
    
    # Date range for analytics (last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # User Analytics
    total_users = User.objects.count()
    users_by_type = User.objects.values('user_type').annotate(count=Count('id')).order_by('user_type')
    new_users_30d = User.objects.filter(date_joined__gte=start_date).count()
    active_users_30d = User.objects.filter(last_login__gte=start_date).count()
    
    # Land Analytics
    total_lands = Land.objects.count()
    lands_by_status = Land.objects.values('approval_status').annotate(count=Count('id'))
    lands_by_location = Land.objects.values('location').annotate(count=Count('id')).order_by('-count')[:10]
    avg_land_size = Land.objects.aggregate(avg_size=Avg('size'))['avg_size'] or 0
    
    # Project Analytics
    total_projects = FarmingProject.objects.count()
    projects_by_status = FarmingProject.objects.values('status').annotate(count=Count('id'))
    projects_by_approval = FarmingProject.objects.values('approval_status').annotate(count=Count('id'))
    avg_project_yield = FarmingProject.objects.aggregate(avg_yield=Avg('estimated_yield'))['avg_yield'] or 0
    
    # Activity Analytics
    total_activities = ActivityLog.objects.count()
    activities_30d = ActivityLog.objects.filter(timestamp__gte=start_date).count()
    activities_by_user = ActivityLog.objects.values('user__username').annotate(count=Count('id')).order_by('-count')[:10]
    
    # Upload Analytics
    total_uploads = ImageUpload.objects.count()
    uploads_30d = ImageUpload.objects.filter(timestamp__gte=start_date).count()
    
    # Recommendation Analytics
    total_recommendations = Recommendation.objects.count()
    recommendations_30d = Recommendation.objects.filter(timestamp__gte=start_date).count()
    
    # Time-based analytics
    daily_users = User.objects.filter(date_joined__gte=start_date).annotate(
        date=TruncDate('date_joined')
    ).values('date').annotate(count=Count('id')).order_by('date')
    
    daily_activities = ActivityLog.objects.filter(timestamp__gte=start_date).annotate(
        date=TruncDate('timestamp')
    ).values('date').annotate(count=Count('id')).order_by('date')
    
    daily_lands = Land.objects.filter(date_listed__gte=start_date).annotate(
        date=TruncDate('date_listed')
    ).values('date').annotate(count=Count('id')).order_by('date')
    
    daily_projects = FarmingProject.objects.filter(start_date__gte=start_date.date()).annotate(
        date=TruncDate('start_date')
    ).values('date').annotate(count=Count('id')).order_by('date')
    
    # Admin Action Analytics
    total_admin_actions = AdminAuditLog.objects.count()
    actions_30d = AdminAuditLog.objects.filter(timestamp__gte=start_date).count()
    actions_by_type = AdminAuditLog.objects.values('action_type').annotate(count=Count('id')).order_by('-count')
    
    # Prepare chart data
    chart_data = {
        'daily_users': list(daily_users),
        'daily_activities': list(daily_activities),
        'daily_lands': list(daily_lands),
        'daily_projects': list(daily_projects),
        'users_by_type': list(users_by_type),
        'lands_by_status': list(lands_by_status),
        'projects_by_status': list(projects_by_status),
        'actions_by_type': list(actions_by_type),
    }
    
    return render(request, 'accounts/admin_analytics.html', {
        'total_users': total_users,
        'users_by_type': users_by_type,
        'new_users_30d': new_users_30d,
        'active_users_30d': active_users_30d,
        'total_lands': total_lands,
        'lands_by_status': lands_by_status,
        'lands_by_location': lands_by_location,
        'avg_land_size': avg_land_size,
        'total_projects': total_projects,
        'projects_by_status': projects_by_status,
        'projects_by_approval': projects_by_approval,
        'avg_project_yield': avg_project_yield,
        'total_activities': total_activities,
        'activities_30d': activities_30d,
        'activities_by_user': activities_by_user,
        'total_uploads': total_uploads,
        'uploads_30d': uploads_30d,
        'total_recommendations': total_recommendations,
        'recommendations_30d': recommendations_30d,
        'total_admin_actions': total_admin_actions,
        'actions_30d': actions_30d,
        'actions_by_type': actions_by_type,
        'chart_data': json.dumps(chart_data),
        'start_date': start_date,
        'end_date': end_date,
    })

@superuser_required
def generate_report(request):
    """Generate downloadable reports"""
    report_type = request.GET.get('type', 'overview')
    
    if report_type == 'user_report':
        users = User.objects.all().order_by('-date_joined')
        return render(request, 'accounts/reports/user_report.html', {'users': users})
    elif report_type == 'land_report':
        lands = Land.objects.all().order_by('-date_listed')
        return render(request, 'accounts/reports/land_report.html', {'lands': lands})
    elif report_type == 'project_report':
        projects = FarmingProject.objects.all().order_by('-start_date')
        return render(request, 'accounts/reports/project_report.html', {'projects': projects})
    elif report_type == 'activity_report':
        activities = ActivityLog.objects.all().order_by('-timestamp')
        return render(request, 'accounts/reports/activity_report.html', {'activities': activities})
    else:
        return redirect('admin_analytics')

def custom_login(request):
    """Custom login view that redirects to home page after successful login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            # Redirect to home page where users can see welcome message and choose their dashboard
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    # Create a simple form context for the template
    from django.contrib.auth.forms import AuthenticationForm
    form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def contact_support(request):
    """Contact support form for users, especially investors"""
    if request.method == 'POST':
        form = ContactSupportForm(request.POST)
        if form.is_valid():
            # Create notification for all superusers about the support request
            superusers = User.objects.filter(is_superuser=True)
            for admin in superusers:
                create_notification(
                    user=admin,
                    notification_type='SYSTEM_MAINTENANCE',  # Using this as closest match
                    title=f'Support Request from {request.user.get_full_name() or request.user.username}',
                    message=f'Subject: {form.cleaned_data["subject"]}\n\n{form.cleaned_data["message"]}\n\nContact: {form.cleaned_data["preferred_contact"]}\nUrgent: {"Yes" if form.cleaned_data["urgent"] else "No"}',
                    related_object_id=request.user.id,
                    related_object_type='User'
                )
            
            messages.success(request, 'Your support request has been submitted successfully. We will get back to you soon!')
            return redirect('home')
    else:
        form = ContactSupportForm()
    
    return render(request, 'accounts/contact_support.html', {
        'form': form,
        **get_notification_data(request.user),
    })
