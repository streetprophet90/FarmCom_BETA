from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from .forms import UserRegistrationForm, UserProfileForm, ImageUploadForm, ActivityLogForm
from .models import ActivityLog, ImageUpload, User
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

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
            login(request, user)
            messages.success(request, f'Welcome to FarmCom, {user.first_name}!')
            return redirect('home')
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
                messages.success(request, 'Image uploaded successfully!')
                return redirect('user_dashboard')
        elif 'log_activity' in request.POST:
            act_form = ActivityLogForm(request.POST)
            if act_form.is_valid():
                activity = act_form.save(commit=False)
                activity.user = user
                activity.save()
                messages.success(request, 'Activity logged successfully!')
                return redirect('user_dashboard')
    # Calculate project progress
    from farming.models import FarmingProject
    user_projects = FarmingProject.objects.filter(
        Q(manager=user) | Q(workers=user)
    ).distinct()
    
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
            from .models import ActivityLog
            try:
                activity = ActivityLog.objects.get(id=activity_id, user__in=workers)
                activity.confirmed = True
                activity.save()
                messages.success(request, 'Activity confirmed!')
            except ActivityLog.DoesNotExist:
                messages.error(request, 'Activity not found or not allowed to confirm.')
            return redirect('farmer_dashboard')
    # Calculate team project progress
    from farming.models import FarmingProject
    team_projects = FarmingProject.objects.filter(
        Q(manager=user) | Q(workers__in=workers)
    ).distinct()
    
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
    })
