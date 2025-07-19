from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CropListing, Order
from accounts.views import create_notification

@login_required
def listing_list(request):
    listings = CropListing.objects.all()
    return render(request, 'marketplace/listing_list.html', {'listings': listings})

@login_required
def order_list(request):
    orders = Order.objects.filter(buyer=request.user)
    return render(request, 'marketplace/order_list.html', {'orders': orders})

@login_required
def create_order(request, listing_id):
    """Create a new order for a crop listing"""
    from django.shortcuts import get_object_or_404
    
    listing = get_object_or_404(CropListing, id=listing_id)
    
    if request.method == 'POST':
        # Create the order
        order = Order.objects.create(
            buyer=request.user,
            listing=listing,
            quantity=request.POST.get('quantity', 1),
            total_price=listing.price_per_unit * float(request.POST.get('quantity', 1))
        )
        
        # Create notification for the seller
        create_notification(
            user=listing.seller,
            notification_type='MARKETPLACE_ORDER',
            title=f'New Order: {listing.crop_name}',
            message=f'You received a new order for {order.quantity} units of {listing.crop_name} from {request.user.get_full_name() or request.user.username}',
            related_object_id=order.id,
            related_object_type='Order'
        )
        
        # Create notification for the buyer
        create_notification(
            user=request.user,
            notification_type='MARKETPLACE_ORDER',
            title=f'Order Placed: {listing.crop_name}',
            message=f'Your order for {order.quantity} units of {listing.crop_name} has been placed successfully.',
            related_object_id=order.id,
            related_object_type='Order'
        )
        
        messages.success(request, 'Order placed successfully!')
        return redirect('order_list')
    
    return render(request, 'marketplace/create_order.html', {'listing': listing})
