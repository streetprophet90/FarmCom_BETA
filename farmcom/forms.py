from django import forms
from .models import CommunityNews

class CommunityNewsForm(forms.ModelForm):
    class Meta:
        model = CommunityNews
        fields = ['title', 'content', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter news title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter news content'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        } 