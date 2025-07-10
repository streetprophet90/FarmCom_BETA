from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CropListing, Order

@login_required
def listing_list(request):
    listings = CropListing.objects.all()
    return render(request, 'marketplace/listing_list.html', {'listings': listings})

@login_required
def order_list(request):
    orders = Order.objects.filter(buyer=request.user)
    return render(request, 'marketplace/order_list.html', {'orders': orders})
