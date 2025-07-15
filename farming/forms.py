from django import forms
from .models import FarmingProject

class FarmingProjectForm(forms.ModelForm):
    class Meta:
        model = FarmingProject
        fields = ['land', 'start_date', 'end_date', 'status', 'crops', 'estimated_yield', 'actual_yield'] 