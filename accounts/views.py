from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from .forms import UserRegistrationForm, UserProfileForm, ImageUploadForm, ActivityLogForm
from .models import ActivityLog, ImageUpload, User
from django.contrib.auth import get_user_model

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
    return render(request, 'accounts/user_dashboard.html', {
        'progress': progress,
        'uploads': uploads,
        'activities': activities,
        'img_form': img_form,
        'act_form': act_form,
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
    return render(request, 'accounts/farmer_dashboard.html', {
        'stats': stats,
        'workers': workers,
        'worker_uploads': worker_uploads,
        'worker_activities': worker_activities,
        'img_form': img_form,
        'act_form': act_form,
    })
