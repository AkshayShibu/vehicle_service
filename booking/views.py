from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Booking

@login_required
def create_booking(request):
    customer = request.user.customer_profile
    vehicles = customer.vehicles.all()
    
    if request.method == 'POST':
        service_type = request.POST.get('service_type')
        preferred_date = request.POST.get('preferred_date')
        preferred_time = request.POST.get('preferred_time')
        problem_description = request.POST.get('problem_description', '')

        Booking.objects.create(
            customer=customer,
            service_type=service_type,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            problem_description=problem_description
        )

        return redirect('customer_dashboard')

    return render(request, 'booking/create_booking.html', {
        'customer': customer,
        'vehicles': vehicles
    })

from django.shortcuts import get_object_or_404
from django.contrib import messages

@login_required
def cancel_booking(request, booking_id):
    """Allow customer to cancel a pending booking"""
    customer = request.user.customer_profile
    booking = get_object_or_404(Booking, id=booking_id, customer=customer)
    
    if booking.status == 'pending':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, f"Booking #{booking.id} has been successfully cancelled.")
    else:
        messages.error(request, f"Cannot cancel booking #{booking.id} because it is already {booking.status}.")
        
    return redirect('customer_dashboard')
