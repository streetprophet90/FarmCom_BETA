from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ImageUpload, ActivityLog, Recommendation


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)
    location = forms.CharField(max_length=100, required=True)
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)
    skills = forms.CharField(max_length=200, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'user_type', 
                  'phone', 'location', 'bio', 'skills', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'location', 'bio', 'skills')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control' 


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageUpload
        fields = ['image', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description (optional)'}),
        }

class ActivityLogForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = ['action', 'details']
        widgets = {
            'action': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Action (e.g. Planted maize)'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Details (optional)'}),
        } 

class RecommendationForm(forms.ModelForm):
    class Meta:
        model = Recommendation
        fields = ['content', 'project', 'land']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Share your recommendation or comment...'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'land': forms.Select(attrs={'class': 'form-select'}),
        } 