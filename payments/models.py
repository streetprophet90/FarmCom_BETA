from django.db import models
from farming.models import FarmingProject


class RevenueShare(models.Model):
    project = models.ForeignKey(FarmingProject, on_delete=models.CASCADE)
    landowner_share = models.DecimalField(max_digits=5, decimal_places=2)  # percentage
    workers_share = models.DecimalField(max_digits=5, decimal_places=2)
    manager_share = models.DecimalField(max_digits=5, decimal_places=2)
    investor_share = models.DecimalField(max_digits=5, decimal_places=2)
    platform_share = models.DecimalField(max_digits=5, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    distribution_date = models.DateField(auto_now_add=True)

    def calculate_shares(self):
        return {
            'landowner': self.total_amount * (self.landowner_share / 100),
            'workers': self.total_amount * (self.workers_share / 100),
            'manager': self.total_amount * (self.manager_share / 100),
            'investor': self.total_amount * (self.investor_share / 100),
            'platform': self.total_amount * (self.platform_share / 100),
        }