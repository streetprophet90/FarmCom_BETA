from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import FarmingProject
from .forms import FarmingProjectForm

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
        from django.contrib import messages
        messages.error(request, 'You do not have permission to start a project.')
        from django.shortcuts import redirect
        return redirect('project_list')
    if request.method == 'POST':
        form = FarmingProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.manager = request.user
            project.save()
            form.save_m2m()
            return redirect('project_list')
    else:
        form = FarmingProjectForm()
    return render(request, 'farming/start_project.html', {'form': form})
