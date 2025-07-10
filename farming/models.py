from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL
from lands.models import Land


class FarmingProject(models.Model):
    STATUS_CHOICES = (
        ('PLANNING', 'Planning'),
        ('ACTIVE', 'Active'),
        ('HARVESTED', 'Harvested'),
        ('COMPLETED', 'Completed'),
    )

    land = models.ForeignKey(Land, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_projects')
    workers = models.ManyToManyField(User, related_name='farming_projects')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNING')
    crops = models.CharField(max_length=200)
    estimated_yield = models.DecimalField(max_digits=10, decimal_places=2)
    actual_yield = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.crops} on {self.land.title}"