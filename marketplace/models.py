from django.db import models
from farming.models import FarmingProject
from django.conf import settings
User = settings.AUTH_USER_MODEL


class CropListing(models.Model):
    project = models.OneToOneField(FarmingProject, on_delete=models.CASCADE)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    available_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    is_organic = models.BooleanField(default=False)
    harvest_date = models.DateField()
    listing_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.crops} from {self.project.land.title}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    listing = models.ForeignKey(CropListing, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_address = models.TextField()

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.listing.price_per_unit
        super().save(*args, **kwargs)