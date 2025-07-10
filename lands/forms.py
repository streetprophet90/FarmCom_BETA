from django import forms
from .models import Land


class LandForm(forms.ModelForm):
    class Meta:
        model = Land
        fields = ['title', 'location', 'size', 'description', 'preferred_crops', 'soil_type', 'water_source']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'preferred_crops': forms.TextInput(attrs={'placeholder': 'e.g., Corn, Soybeans, Wheat'}),
        } 