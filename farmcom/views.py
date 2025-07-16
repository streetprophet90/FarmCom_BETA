from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from lands.models import Land
from farming.models import FarmingProject
from marketplace.models import CropListing
from accounts.models import User
from .models import CommunityNews
from .forms import CommunityNewsForm

def home(request):
    if request.user.is_authenticated:
        # Redirect authenticated users to the logged-in home page
        return redirect('logged_in_home')
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

@login_required
def logged_in_home(request):
    """Dedicated view for logged-in users' home page"""
    user = request.user
    # Get active news from database
    news = CommunityNews.objects.filter(is_active=True).order_by('-created_at')[:5]
    return render(request, 'home_logged_in.html', {
        'user': user,
        'news': news,
    })

def contact_support(request):
    if request.method == 'POST':
        # In a real app, handle sending email or saving the message
        return render(request, 'contact_support.html', {'success': True})
    return render(request, 'contact_support.html')

# Superuser-only views for managing community news
def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def community_news_list(request):
    """List all community news items"""
    news_items = CommunityNews.objects.all().order_by('-created_at')
    return render(request, 'farmcom/community_news_list.html', {
        'news_items': news_items
    })

@user_passes_test(is_superuser)
def community_news_create(request):
    """Create a new community news item"""
    if request.method == 'POST':
        form = CommunityNewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.created_by = request.user
            news.save()
            messages.success(request, 'News item created successfully!')
            return redirect('farmcom:community_news_list')
    else:
        form = CommunityNewsForm()
    
    return render(request, 'farmcom/community_news_form.html', {
        'form': form,
        'title': 'Create News Item'
    })

@user_passes_test(is_superuser)
def community_news_edit(request, pk):
    """Edit an existing community news item"""
    news = get_object_or_404(CommunityNews, pk=pk)
    if request.method == 'POST':
        form = CommunityNewsForm(request.POST, instance=news)
        if form.is_valid():
            form.save()
            messages.success(request, 'News item updated successfully!')
            return redirect('farmcom:community_news_list')
    else:
        form = CommunityNewsForm(instance=news)
    
    return render(request, 'farmcom/community_news_form.html', {
        'form': form,
        'news': news,
        'title': 'Edit News Item'
    })

@user_passes_test(is_superuser)
def community_news_delete(request, pk):
    """Delete a community news item"""
    news = get_object_or_404(CommunityNews, pk=pk)
    if request.method == 'POST':
        news.delete()
        messages.success(request, 'News item deleted successfully!')
        return redirect('farmcom:community_news_list')
    
    return render(request, 'farmcom/community_news_confirm_delete.html', {
        'news': news
    })

@user_passes_test(is_superuser)
def community_news_toggle_active(request, pk):
    """Toggle the active status of a news item via AJAX"""
    if request.method == 'POST' and request.is_ajax():
        news = get_object_or_404(CommunityNews, pk=pk)
        news.is_active = not news.is_active
        news.save()
        return JsonResponse({
            'success': True,
            'is_active': news.is_active
        })
    return JsonResponse({'success': False}) 