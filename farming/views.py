from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from .models import FarmingProject
from .forms import FarmingProjectForm
from accounts.views import create_notification
from accounts.models import User

@login_required
def project_list(request):
    user = request.user
    if user.is_superuser:
        projects = FarmingProject.objects.all()
    else:
        projects = FarmingProject.objects.filter(approval_status='APPROVED')
    return render(request, 'farming/project_list.html', {'projects': projects})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(FarmingProject, pk=pk)
    if not request.user.is_superuser and project.approval_status != 'APPROVED':
        return render(request, 'farming/project_detail.html', {'error': 'This project is not available.'})
    return render(request, 'farming/project_detail.html', {'project': project})

@login_required
def start_project(request):
    if not (request.user.is_superuser or getattr(request.user, 'user_type', None) == 'FARMER'):
        messages.error(request, 'You do not have permission to start a project.')
        return redirect('project_list')
    
    if request.method == 'POST':
        form = FarmingProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.manager = request.user
            project.save()
            form.save_m2m()
            
            # Create notification for all superusers about new project
            superusers = User.objects.filter(is_superuser=True)
            for admin in superusers:
                create_notification(
                    user=admin,
                    notification_type='PROJECT_PENDING',
                    title=f'New Project: {project.crops}',
                    message=f'Farmer {request.user.get_full_name() or request.user.username} created a new project: {project.crops}',
                    related_object_id=project.id,
                    related_object_type='FarmingProject'
                )
            
            # Create notification for project manager
            create_notification(
                user=request.user,
                notification_type='PROJECT_UPDATE',
                title=f'Project Created: {project.crops}',
                message=f'Your project "{project.crops}" has been created and is pending approval.',
                related_object_id=project.id,
                related_object_type='FarmingProject'
            )
            
            messages.success(request, 'Project created successfully! It is now pending approval.')
            return redirect('project_list')
    else:
        form = FarmingProjectForm()
    
    return render(request, 'farming/start_project.html', {'form': form})

@login_required
def update_project_status(request, pk):
    """Update project status with notifications"""
    project = get_object_or_404(FarmingProject, pk=pk)
    
    # Check if user has permission to update this project
    if not (request.user.is_superuser or project.manager == request.user):
        messages.error(request, 'You do not have permission to update this project.')
        return redirect('project_detail', pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status != project.status:
            old_status = project.status
            project.status = new_status
            project.save()
            
            # Create notification for project manager
            if project.manager != request.user:
                create_notification(
                    user=project.manager,
                    notification_type='PROJECT_UPDATE',
                    title=f'Project Status Updated: {project.crops}',
                    message=f'Project "{project.crops}" status changed from {old_status} to {new_status}',
                    related_object_id=project.id,
                    related_object_type='FarmingProject'
                )
            
            # Create notification for all workers on the project
            for worker in project.workers.all():
                if worker != request.user:
                    create_notification(
                        user=worker,
                        notification_type='PROJECT_UPDATE',
                        title=f'Project Status Updated: {project.crops}',
                        message=f'Project "{project.crops}" status changed from {old_status} to {new_status}',
                        related_object_id=project.id,
                        related_object_type='FarmingProject'
                    )
            
            messages.success(request, f'Project status updated to {new_status}')
        else:
            messages.warning(request, 'No status change detected.')
        
        return redirect('project_detail', pk=pk)
    
    return render(request, 'farming/update_project_status.html', {'project': project})
