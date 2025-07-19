from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category, Topic, Post, PostLike, TopicSubscription, TopicRequest
from .forms import TopicForm, PostForm, CategoryForm, TopicRequestForm

def category_list(request):
    """Display all forum categories"""
    categories = Category.objects.filter(is_active=True)
    recent_topics = Topic.objects.all().order_by('-created_at')[:10]
    context = {
        'categories': categories,
        'recent_topics': recent_topics,
    }
    return render(request, 'forums/category_list.html', context)

def topic_list(request, category_slug=None):
    """Display topics, optionally filtered by category"""
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        topics = Topic.objects.filter(category=category)
    else:
        category = None
        topics = Topic.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        topics = topics.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(topics, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'topics': page_obj,
        'search_query': search_query,
    }
    return render(request, 'forums/topic_list.html', context)

def topic_detail(request, topic_id):
    """Display a single topic with all its posts"""
    topic = get_object_or_404(Topic, id=topic_id)
    
    # Increment view count
    topic.increment_views()
    
    # Get posts for this topic
    posts = topic.posts.all()
    
    # Pagination for posts
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Check if user is subscribed
    is_subscribed = False
    if request.user.is_authenticated:
        is_subscribed = TopicSubscription.objects.filter(user=request.user, topic=topic).exists()
    
    context = {
        'topic': topic,
        'posts': page_obj,
        'is_subscribed': is_subscribed,
    }
    return render(request, 'forums/topic_detail.html', context)

@login_required
def create_topic(request, category_slug=None):
    """Create a new topic - Only for superusers and users with forum management permissions"""
    # Check if user is superuser or has forum management permission
    from user_permissions.utils import has_permission
    
    if not (request.user.is_superuser or has_permission(request.user, 'FORUM_MANAGEMENT', 'create_topics', 'create')):
        messages.error(request, 'Only administrators can create new topics. Please contact an admin if you need a new topic created.')
        return redirect('home')
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
    else:
        category = None
    
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            if category:
                topic.category = category
            topic.save()
            messages.success(request, 'Topic created successfully!')
            return redirect('topic_detail', topic_id=topic.id)
    else:
        form = TopicForm()
        if category:
            form.fields['category'].initial = category
    
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'forums/create_topic.html', context)

@login_required
def edit_topic(request, topic_id):
    """Edit an existing topic - restricted to superusers and users with forum management permissions"""
    from user_permissions.utils import has_permission
    
    if not (request.user.is_superuser or has_permission(request.user, 'FORUM_MANAGEMENT', 'edit_topics', 'update')):
        messages.error(request, 'Only administrators can edit topics.')
        return redirect('forums:topic_detail', topic_id=topic_id)
    
    topic = get_object_or_404(Topic, id=topic_id)
    
    if request.method == 'POST':
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            messages.success(request, 'Topic updated successfully!')
            return redirect('forums:topic_detail', topic_id=topic.id)
    else:
        form = TopicForm(instance=topic)
    
    context = {
        'form': form,
        'topic': topic,
    }
    return render(request, 'forums/edit_topic.html', context)

@login_required
def delete_topic(request, topic_id):
    """Delete a topic - restricted to superusers and users with forum management permissions"""
    from user_permissions.utils import has_permission
    
    if not (request.user.is_superuser or has_permission(request.user, 'FORUM_MANAGEMENT', 'delete_topics', 'delete')):
        messages.error(request, 'Only administrators can delete topics.')
        return redirect('forums:topic_detail', topic_id=topic_id)
    
    topic = get_object_or_404(Topic, id=topic_id)
    
    if request.method == 'POST':
        category = topic.category
        topic.delete()
        messages.success(request, 'Topic deleted successfully!')
        return redirect('forums:category_topics', category_slug=category.slug)
    
    context = {
        'topic': topic,
    }
    return render(request, 'forums/delete_topic.html', context)

@login_required
def create_post(request, topic_id):
    """Create a new post in a topic"""
    topic = get_object_or_404(Topic, id=topic_id)
    
    if topic.is_locked:
        messages.error(request, 'This topic is locked. You cannot post here.')
        return redirect('topic_detail', topic_id=topic.id)
    
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.author = request.user
            post.save()
            messages.success(request, 'Post added successfully!')
            return redirect('topic_detail', topic_id=topic.id)
    else:
        form = PostForm()
    
    context = {
        'form': form,
        'topic': topic,
    }
    return render(request, 'forums/create_post.html', context)

@login_required
def like_post(request, post_id):
    """Like or unlike a post"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        like, created = PostLike.objects.get_or_create(
            post=post,
            user=request.user
        )
        
        if not created:
            # User already liked, so unlike
            like.delete()
            liked = False
        else:
            liked = True
        
        return JsonResponse({
            'liked': liked,
            'likes_count': post.get_likes_count()
        })
    
    return JsonResponse({'error': 'Invalid request'})

@login_required
def subscribe_topic(request, topic_id):
    """Subscribe or unsubscribe from a topic"""
    topic = get_object_or_404(Topic, id=topic_id)
    
    if request.method == 'POST':
        subscription, created = TopicSubscription.objects.get_or_create(
            topic=topic,
            user=request.user
        )
        
        if not created:
            # User already subscribed, so unsubscribe
            subscription.delete()
            subscribed = False
            messages.success(request, 'Unsubscribed from topic.')
        else:
            subscribed = True
            messages.success(request, 'Subscribed to topic!')
        
        return redirect('topic_detail', topic_id=topic.id)
    
    return redirect('topic_detail', topic_id=topic.id)

@login_required
def mark_solution(request, post_id):
    """Mark a post as the solution to a topic"""
    post = get_object_or_404(Post, id=post_id)
    
    # Only topic author can mark solutions
    if request.user != post.topic.author:
        messages.error(request, 'Only the topic author can mark solutions.')
        return redirect('topic_detail', topic_id=post.topic.id)
    
    if request.method == 'POST':
        # Unmark any existing solutions
        Post.objects.filter(topic=post.topic, is_solution=True).update(is_solution=False)
        
        # Mark this post as solution
        post.is_solution = True
        post.save()
        
        messages.success(request, 'Post marked as solution!')
        return redirect('topic_detail', topic_id=post.topic.id)
    
    return redirect('topic_detail', topic_id=post.topic.id)

def search_topics(request):
    """Search topics across all categories"""
    search_query = request.GET.get('q', '')
    topics = []
    
    if search_query:
        topics = Topic.objects.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(topics, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'topics': page_obj,
        'search_query': search_query,
    }
    return render(request, 'forums/search_results.html', context)

@login_required
def request_topic(request):
    """Request a new topic - for regular users"""
    if request.user.is_superuser:
        messages.info(request, 'As an administrator, you can create topics directly. Use the "New Topic" button instead.')
        return redirect('forums:category_list')
    
    if request.method == 'POST':
        form = TopicRequestForm(request.POST)
        if form.is_valid():
            topic_request = form.save(commit=False)
            topic_request.user = request.user
            topic_request.save()
            
            # Send notifications to all superusers
            from django.contrib.auth import get_user_model
            User = get_user_model()
            superusers = User.objects.filter(is_superuser=True)
            
            for admin in superusers:
                if admin != request.user:  # Don't notify the user who made the request if they're also an admin
                    from accounts.views import create_notification
                    create_notification(
                        user=admin,
                        title=f"New Topic Request: {topic_request.title}",
                        message=f"{request.user.username} has requested a new topic '{topic_request.title}' in the {topic_request.category.name} category. Please review it in the admin panel.",
                        notification_type='TOPIC_REQUEST'
                    )
            
            messages.success(request, 'Topic request submitted successfully! An administrator will review it and get back to you.')
            return redirect('forums:category_list')
    else:
        form = TopicRequestForm()
    
    context = {
        'form': form,
    }
    return render(request, 'forums/request_topic.html', context)

@login_required
def my_topic_requests(request):
    """View user's own topic requests"""
    if request.user.is_superuser:
        # Admins see all requests
        requests = TopicRequest.objects.all()
    else:
        # Regular users see only their own requests
        requests = TopicRequest.objects.filter(user=request.user)
    
    context = {
        'requests': requests,
    }
    return render(request, 'forums/my_topic_requests.html', context)
