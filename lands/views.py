from django.shortcuts import render,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView
from django.db.models import Q

from .models import Land
from .forms import LandForm


class LandListView(ListView):
    model = Land
    template_name = 'lands/land_list.html'
    context_object_name = 'lands'

    def get_queryset(self):
        queryset = Land.objects.filter(is_available=True)
        
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
        
        # Get unique values for filter dropdowns
        context['soil_types'] = Land.objects.filter(is_available=True).values_list('soil_type', flat=True).distinct()
        context['crop_types'] = Land.objects.filter(is_available=True).values_list('preferred_crops', flat=True).distinct()
        context['locations'] = Land.objects.filter(is_available=True).values_list('location', flat=True).distinct()
        
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
    return render(request, 'lands/land_detail.html', {'land': land})


class AddLandView(CreateView):
    model = Land
    form_class = LandForm
    template_name = 'lands/add_land.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)