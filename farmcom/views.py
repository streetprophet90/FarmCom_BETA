from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from lands.models import Land
from farming.models import FarmingProject
from marketplace.models import CropListing
from accounts.models import User

def home(request):
    if request.user.is_authenticated:
        # Show logged-in home with welcome, dashboard/profile buttons, and news
        user = request.user
        # Example news (static for now)
        news = [
            {"title": "FarmCom Launches New Dashboard!", "content": "Monitor your progress and team with our new dashboards."},
            {"title": "Upcoming Community Event", "content": "Join us for the annual FarmCom networking event this August."},
            {"title": "Tips for Sustainable Farming", "content": "Check out our latest blog post on sustainable agriculture practices."},
        ]
        return render(request, 'home_logged_in.html', {
            'user': user,
            'news': news,
        })
    else:
        # Show the public home page with counters
        context = {
            'total_lands': Land.objects.count(),
            'total_projects': FarmingProject.objects.count(),
            'total_listings': CropListing.objects.count(),
            'total_users': User.objects.count(),
            'recent_lands': Land.objects.order_by('-id')[:5],
            'recent_projects': FarmingProject.objects.order_by('-id')[:5],
        }
        return render(request, 'home.html', context) 