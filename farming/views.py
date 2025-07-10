from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import FarmingProject

@login_required
def project_list(request):
    projects = FarmingProject.objects.all()
    return render(request, 'farming/project_list.html', {'projects': projects})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(FarmingProject, pk=pk)
    return render(request, 'farming/project_detail.html', {'project': project})
