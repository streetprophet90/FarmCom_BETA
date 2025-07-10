from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import RevenueShare

@login_required
def revenue_share_list(request):
    revenue_shares = RevenueShare.objects.all()
    return render(request, 'payments/revenue_share_list.html', {'revenue_shares': revenue_shares})
