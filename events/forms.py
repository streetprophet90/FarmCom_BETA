from django import forms
from django.contrib.auth import get_user_model
from .models import Event, EventRegistration, EventComment, EventCategory

User = get_user_model()

class EventForm(forms.ModelForm):
    """Form for creating and editing events"""
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'short_description', 'event_type', 'category', 
            'access_level', 'venue_name', 'address', 'city', 'region', 'coordinates',
            'start_date', 'start_time', 'end_date', 'end_time', 'registration_deadline',
            'max_participants', 'is_registration_required', 'is_free', 'price', 'currency',
            'contact_email', 'contact_phone', 'website', 'featured_image', 'status',
            'meta_title', 'meta_description'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter event title...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Describe your event...'
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description for listings...'
            }),
            'event_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'access_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'venue_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Venue name...'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Full address...'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City...'
            }),
            'region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Region...'
            }),
            'coordinates': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Latitude,Longitude (optional)'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'registration_deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'max_participants': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank for unlimited'
            }),
            'is_registration_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_free': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-control'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@example.com'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+233 XX XXX XXXX'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO title (optional)'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'SEO description (optional)'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date.")
        
        if start_date == end_date and start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")
        
        return cleaned_data

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description.strip()) < 50:
            raise forms.ValidationError("Event description must be at least 50 characters long.")
        return description

class EventRegistrationForm(forms.ModelForm):
    """Form for event registration"""
    
    class Meta:
        model = EventRegistration
        fields = ['dietary_restrictions', 'special_requirements', 'emergency_contact', 'emergency_phone']
        widgets = {
            'dietary_restrictions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any dietary restrictions or preferences...'
            }),
            'special_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requirements or accommodations...'
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact name'
            }),
            'emergency_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact phone'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        registration = super().save(commit=False)
        if self.event:
            registration.event = self.event
        if self.user:
            registration.user = self.user
        if commit:
            registration.save()
        return registration

class EventCommentForm(forms.ModelForm):
    """Form for adding comments to events"""
    
    class Meta:
        model = EventComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your comment here...'
            })
        }

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 10:
            raise forms.ValidationError("Comment must be at least 10 characters long.")
        return content

    def save(self, commit=True):
        comment = super().save(commit=False)
        if self.event:
            comment.event = self.event
        if self.user:
            comment.author = self.user
        if commit:
            comment.save()
        return comment

class EventReplyForm(EventCommentForm):
    """Form for replying to comments"""
    
    def __init__(self, *args, **kwargs):
        self.parent_comment = kwargs.pop('parent_comment', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        comment = super().save(commit=False)
        if self.parent_comment:
            comment.parent = self.parent_comment
        if commit:
            comment.save()
        return comment

class EventSearchForm(forms.Form):
    """Form for searching events"""
    
    SORT_CHOICES = [
        ('newest', 'Newest First'),
        ('oldest', 'Oldest First'),
        ('popular', 'Most Popular'),
        ('views', 'Most Viewed'),
        ('registrations', 'Most Registrations'),
    ]
    
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search events...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=EventCategory.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    event_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Event.TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    access_level = forms.ChoiceField(
        choices=[('', 'All Access Levels')] + Event.ACCESS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    is_free = forms.ChoiceField(
        choices=[
            ('', 'All Events'),
            ('True', 'Free Events Only'),
            ('False', 'Paid Events Only'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        initial='newest',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    featured_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

class EventCategoryForm(forms.ModelForm):
    """Form for creating and editing event categories"""
    
    class Meta:
        model = EventCategory
        fields = ['name', 'description', 'icon', 'color', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category name...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Category description...'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Font Awesome icon class (e.g., fas fa-calendar)'
            }),
            'color': forms.Select(attrs={
                'class': 'form-control'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add color choices
        self.fields['color'].choices = [
            ('primary', 'Primary (Blue)'),
            ('secondary', 'Secondary (Gray)'),
            ('success', 'Success (Green)'),
            ('danger', 'Danger (Red)'),
            ('warning', 'Warning (Yellow)'),
            ('info', 'Info (Cyan)'),
            ('light', 'Light'),
            ('dark', 'Dark'),
        ] 