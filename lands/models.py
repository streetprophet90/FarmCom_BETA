from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL


class Land(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lands')
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    size = models.DecimalField(max_digits=10, decimal_places=2)  # in acres
    description = models.TextField()
    is_available = models.BooleanField(default=True)
    preferred_crops = models.CharField(max_length=200)
    soil_type = models.CharField(max_length=50)
    water_source = models.CharField(max_length=50)
    date_listed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.size} acres) in {self.location}"