from django.shortcuts import render
from lands.models import Land
from farming.models import FarmingProject
from marketplace.models import CropListing
from accounts.models import User

def home(request):
    # Get counts from database
    total_lands = Land.objects.count()
    total_projects = FarmingProject.objects.count()
    total_listings = CropListing.objects.count()
    total_users = User.objects.count()
    
    # Get some recent data for display
    recent_lands = Land.objects.filter(is_available=True).order_by('-id')[:3]
    recent_projects = FarmingProject.objects.filter(status='ACTIVE').order_by('-id')[:3]
    
    context = {
        'total_lands': total_lands,
        'total_projects': total_projects,
        'total_listings': total_listings,
        'total_users': total_users,
        'recent_lands': recent_lands,
        'recent_projects': recent_projects,
    }
    
    return render(request, 'home.html', context) 