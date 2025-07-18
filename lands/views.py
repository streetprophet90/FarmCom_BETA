from django.shortcuts import render,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView
from django.db.models import Q
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse

from .models import Land
from .forms import LandForm
from accounts.views import create_notification


class LandListView(ListView):
    model = Land
    template_name = 'lands/land_list.html'
    context_object_name = 'lands'

    def get_queryset(self):
        queryset = Land.objects.filter(is_available=True)
        user = self.request.user
        if not user.is_authenticated or not user.is_superuser:
            queryset = queryset.filter(approval_status='APPROVED')
        
        # Get filter parameters from request
        soil_type = self.request.GET.get('soil_type')
        min_size = self.request.GET.get('min_size')
        max_size = self.request.GET.get('max_size')
        crop_type = self.request.GET.get('crop_type')
        location = self.request.GET.get('location')
        
        # Apply filters
        if soil_type:
            queryset = queryset.filter(soil_type__icontains=soil_type)
        
        if min_size:
            queryset = queryset.filter(size__gte=float(min_size))
        
        if max_size:
            queryset = queryset.filter(size__lte=float(max_size))
        
        if crop_type:
            queryset = queryset.filter(preferred_crops__icontains=crop_type)
        
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        base_qs = Land.objects.filter(is_available=True)
        if not user.is_authenticated or not user.is_superuser:
            base_qs = base_qs.filter(approval_status='APPROVED')
        # Get unique values for filter dropdowns
        context['soil_types'] = base_qs.values_list('soil_type', flat=True).distinct()
        context['crop_types'] = base_qs.values_list('preferred_crops', flat=True).distinct()
        context['locations'] = base_qs.values_list('location', flat=True).distinct()
        
        # Get current filter values
        context['current_soil'] = self.request.GET.get('soil_type', '')
        context['current_min_size'] = self.request.GET.get('min_size', '')
        context['current_max_size'] = self.request.GET.get('max_size', '')
        context['current_crop'] = self.request.GET.get('crop_type', '')
        context['current_location'] = self.request.GET.get('location', '')
        
        return context


@login_required
def land_detail(request, pk):
    land = get_object_or_404(Land, pk=pk)
    if not request.user.is_superuser and land.approval_status != 'APPROVED':
        return render(request, 'lands/land_detail.html', {'error': 'This land is not available.'})
    return render(request, 'lands/land_detail.html', {'land': land})


class AddLandView(UserPassesTestMixin, CreateView):
    model = Land
    form_class = LandForm
    template_name = 'lands/add_land.html'
    success_url = '/lands/'

    def test_func(self):
        return self.request.user.is_superuser or getattr(self.request.user, 'user_type', None) == 'LANDOWNER'

    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to add land.')
        from django.shortcuts import redirect
        return redirect('land_list')
    
    def form_valid(self, form):
        land = form.save(commit=False)
        land.owner = self.request.user
        land.save()
        
        # Create notification for all superusers about new land
        from accounts.models import User
        superusers = User.objects.filter(is_superuser=True)
        for admin in superusers:
            create_notification(
                user=admin,
                notification_type='LAND_PENDING',
                title=f'New Land: {land.title}',
                message=f'Landowner {self.request.user.get_full_name() or self.request.user.username} added new land: {land.title}',
                related_object_id=land.id,
                related_object_type='Land'
            )
        
        # Create notification for land owner
        create_notification(
            user=self.request.user,
            notification_type='LAND_PENDING',
            title=f'Land Added: {land.title}',
            message=f'Your land "{land.title}" has been added and is pending approval.',
            related_object_id=land.id,
            related_object_type='Land'
        )
        
        messages.success(self.request, 'Land added successfully! It is now pending approval.')
        return super().form_valid(form)