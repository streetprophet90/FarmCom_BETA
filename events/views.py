from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q, Count, F
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Event, EventCategory, EventRegistration, EventComment, EventLike, EventView
from .forms import EventForm, EventRegistrationForm, EventCommentForm, EventReplyForm, EventSearchForm
from accounts.notification_utils import create_enhanced_notification

User = get_user_model()

class EventListView(ListView):
    """Display list of published events with search and filtering"""
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 12

    def get_queryset(self):
        queryset = Event.objects.filter(
            status='PUBLISHED',
            start_date__gte=timezone.now().date()
        ).select_related('organizer', 'category').prefetch_related('user_likes')
        
        # Apply search and filters
        form = EventSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            category = form.cleaned_data.get('category')
            event_type = form.cleaned_data.get('event_type')
            access_level = form.cleaned_data.get('access_level')
            is_free = form.cleaned_data.get('is_free')
            sort_by = form.cleaned_data.get('sort_by')
            featured_only = form.cleaned_data.get('featured_only')
            
            # Search functionality
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(organizer__username__icontains=query) |
                    Q(venue_name__icontains=query) |
                    Q(city__icontains=query)
                )
            
            # Filters
            if category:
                queryset = queryset.filter(category=category)
            
            if event_type:
                queryset = queryset.filter(event_type=event_type)
            
            if access_level:
                queryset = queryset.filter(access_level=access_level)
            
            if is_free is not None:
                queryset = queryset.filter(is_free=is_free)
            
            if featured_only:
                queryset = queryset.filter(featured=True)
            
            # Sorting
            if sort_by == 'oldest':
                queryset = queryset.order_by('start_date')
            elif sort_by == 'popular':
                queryset = queryset.order_by('-views', '-registrations_count')
            elif sort_by == 'views':
                queryset = queryset.order_by('-views')
            elif sort_by == 'registrations':
                queryset = queryset.order_by('-registrations_count')
            else:  # newest
                queryset = queryset.order_by('start_date')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = EventSearchForm(self.request.GET)
        context['categories'] = EventCategory.objects.filter(is_active=True)
        context['featured_events'] = Event.objects.filter(
            status='PUBLISHED',
            featured=True,
            start_date__gte=timezone.now().date()
        ).select_related('organizer', 'category')[:6]
        return context

class EventDetailView(DetailView):
    """Display individual event with registration and comments"""
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        return Event.objects.filter(
            status='PUBLISHED'
        ).select_related('organizer', 'category').prefetch_related('comments__author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        
        # Track view
        if self.request.user.is_authenticated:
            EventView.objects.get_or_create(
                event=event,
                user=self.request.user,
                defaults={'ip_address': self.request.META.get('REMOTE_ADDR')}
            )
        else:
            EventView.objects.get_or_create(
                event=event,
                ip_address=self.request.META.get('REMOTE_ADDR'),
                defaults={'user_agent': self.request.META.get('HTTP_USER_AGENT', '')}
            )
        
        # Increment view count
        event.increment_views()
        
        # Get approved comments
        context['comments'] = event.comments.filter(is_approved=True, parent=None)
        context['comment_form'] = EventCommentForm(event=event, user=self.request.user)
        context['registration_form'] = EventRegistrationForm(event=event, user=self.request.user)
        
        # Check if user has liked/registered
        if self.request.user.is_authenticated:
            context['user_liked'] = EventLike.objects.filter(
                event=event, user=self.request.user
            ).exists()
            context['user_registered'] = EventRegistration.objects.filter(
                event=event, user=self.request.user
            ).exists()
            if context['user_registered']:
                context['registration'] = EventRegistration.objects.get(
                    event=event, user=self.request.user
                )
        
        # Related events
        context['related_events'] = Event.objects.filter(
            status='PUBLISHED',
            category=event.category,
            start_date__gte=timezone.now().date()
        ).exclude(id=event.id)[:4]
        
        return context

class CategoryDetailView(ListView):
    """Display events by category"""
    model = Event
    template_name = 'events/category_detail.html'
    context_object_name = 'events'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(EventCategory, slug=self.kwargs['slug'], is_active=True)
        return Event.objects.filter(
            category=self.category,
            status='PUBLISHED',
            start_date__gte=timezone.now().date()
        ).select_related('organizer').order_by('start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

class EventCreateView(LoginRequiredMixin, CreateView):
    """Create new event"""
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('events:event_list')

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        response = super().form_valid(form)
        
        # Create notification for new event
        if form.instance.status == 'PUBLISHED':
            create_enhanced_notification(
                user=self.request.user,
                notification_type='Event Published',
                title=f'Event "{form.instance.title}" published',
                message=f'Your event "{form.instance.title}" has been published successfully.',
                related_object=form.instance
            )
        
        messages.success(self.request, 'Event created successfully!')
        return response

class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update existing event"""
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer or self.request.user.is_superuser

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Event updated successfully!')
        return response

class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete event"""
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('events:event_list')

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer or self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Event deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
@require_POST
def like_event(request, event_id):
    """Like/unlike an event"""
    event = get_object_or_404(Event, id=event_id)
    like, created = EventLike.objects.get_or_create(
        event=event, user=request.user
    )
    
    if created:
        liked = True
    else:
        like.delete()
        liked = False
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked})
    
    return HttpResponseRedirect(event.get_absolute_url())

@login_required
@require_POST
def register_event(request, event_id):
    """Register for an event"""
    event = get_object_or_404(Event, id=event_id)
    
    if not event.can_register():
        messages.error(request, 'Registration is not available for this event.')
        return HttpResponseRedirect(event.get_absolute_url())
    
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, 'You are already registered for this event.')
        return HttpResponseRedirect(event.get_absolute_url())
    
    if request.method == 'POST':
        form = EventRegistrationForm(request.POST, event=event, user=request.user)
        if form.is_valid():
            registration = form.save()
            
            # Create notification for event organizer
            if registration.user != event.organizer:
                create_enhanced_notification(
                    user=event.organizer,
                    notification_type='New Event Registration',
                    title=f'New registration for "{event.title}"',
                    message=f'{registration.user.username} registered for your event.',
                    related_object=registration
                )
            
            messages.success(request, 'Successfully registered for the event!')
            return redirect(event.get_absolute_url())
    else:
        form = EventRegistrationForm(event=event, user=request.user)
    
    return render(request, 'events/event_detail.html', {
        'event': event,
        'registration_form': form
    })

@login_required
@require_POST
def unregister_event(request, event_id):
    """Unregister from an event"""
    event = get_object_or_404(Event, id=event_id)
    registration = get_object_or_404(EventRegistration, event=event, user=request.user)
    
    registration.delete()
    messages.success(request, 'Successfully unregistered from the event.')
    
    return HttpResponseRedirect(event.get_absolute_url())

@login_required
def add_comment(request, event_id):
    """Add comment to event"""
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = EventCommentForm(request.POST, event=event, user=request.user)
        if form.is_valid():
            comment = form.save()
            
            # Create notification for event organizer
            if comment.author != event.organizer:
                create_enhanced_notification(
                    user=event.organizer,
                    notification_type='New Event Comment',
                    title=f'New comment on "{event.title}"',
                    message=f'{comment.author.username} commented on your event.',
                    related_object=comment
                )
            
            messages.success(request, 'Comment added successfully!')
            return redirect(event.get_absolute_url())
    else:
        form = EventCommentForm(event=event, user=request.user)
    
    return render(request, 'events/event_detail.html', {
        'event': event,
        'comment_form': form
    })

@login_required
def add_reply(request, comment_id):
    """Add reply to comment"""
    parent_comment = get_object_or_404(EventComment, id=comment_id)
    event = parent_comment.event
    
    if request.method == 'POST':
        form = EventReplyForm(request.POST, event=event, user=request.user, parent_comment=parent_comment)
        if form.is_valid():
            reply = form.save()
            
            # Create notification for parent comment author
            if reply.author != parent_comment.author:
                create_enhanced_notification(
                    user=parent_comment.author,
                    notification_type='New Event Reply',
                    title=f'New reply to your comment',
                    message=f'{reply.author.username} replied to your comment on "{event.title}".',
                    related_object=reply
                )
            
            messages.success(request, 'Reply added successfully!')
            return redirect(event.get_absolute_url())
    else:
        form = EventReplyForm(event=event, user=request.user, parent_comment=parent_comment)
    
    return render(request, 'events/event_detail.html', {
        'event': event,
        'reply_form': form,
        'parent_comment': parent_comment
    })

@login_required
def my_events(request):
    """Display user's organized events"""
    events = Event.objects.filter(organizer=request.user).order_by('-created_at')
    paginator = Paginator(events, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'events/my_events.html', {
        'page_obj': page_obj,
        'events': page_obj
    })

@login_required
def my_registrations(request):
    """Display user's event registrations"""
    registrations = EventRegistration.objects.filter(user=request.user).select_related('event__organizer', 'event__category')
    paginator = Paginator(registrations, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'events/my_registrations.html', {
        'page_obj': page_obj,
        'registrations': page_obj
    })

def search_events(request):
    """Advanced search for events"""
    form = EventSearchForm(request.GET)
    events = []
    
    if form.is_valid() and any(form.cleaned_data.values()):
        events = Event.objects.filter(
            status='PUBLISHED',
            start_date__gte=timezone.now().date()
        ).select_related('organizer', 'category')
        
        # Apply search filters
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        event_type = form.cleaned_data.get('event_type')
        access_level = form.cleaned_data.get('access_level')
        is_free = form.cleaned_data.get('is_free')
        sort_by = form.cleaned_data.get('sort_by')
        featured_only = form.cleaned_data.get('featured_only')
        
        if query:
            events = events.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(organizer__username__icontains=query) |
                Q(venue_name__icontains=query) |
                Q(city__icontains=query)
            )
        
        if category:
            events = events.filter(category=category)
        
        if event_type:
            events = events.filter(event_type=event_type)
        
        if access_level:
            events = events.filter(access_level=access_level)
        
        if is_free is not None:
            events = events.filter(is_free=is_free)
        
        if featured_only:
            events = events.filter(featured=True)
        
        # Sorting
        if sort_by == 'oldest':
            events = events.order_by('start_date')
        elif sort_by == 'popular':
            events = events.order_by('-views', '-registrations_count')
        elif sort_by == 'views':
            events = events.order_by('-views')
        elif sort_by == 'registrations':
            events = events.order_by('-registrations_count')
        else:
            events = events.order_by('start_date')
    
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'events/search_results.html', {
        'form': form,
        'page_obj': page_obj,
        'events': page_obj,
        'search_performed': form.is_valid() and any(form.cleaned_data.values())
    })

def event_calendar(request):
    """Display events in calendar view"""
    events = Event.objects.filter(
        status='PUBLISHED',
        start_date__gte=timezone.now().date()
    ).select_related('organizer', 'category').order_by('start_date')
    
    return render(request, 'events/event_calendar.html', {
        'events': events
    })
