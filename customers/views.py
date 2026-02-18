from django.contrib.auth.decorators import login_required
from .models import Customer
from django.shortcuts import render, redirect
from .models import Vehicle

@login_required
def customer_dashboard(request):
    customer = request.user.customer_profile
    vehicles = customer.vehicles.all()
    
    # Get all bookings for this customer
    from booking.models import Booking
    
    # Active bookings (pending, approved, in_progress)
    active_bookings = Booking.objects.filter(
        customer=customer,
        status__in=['pending', 'approved', 'in_progress']
    ).order_by('-created_at')
    
    # Completed bookings (completed, cancelled)
    completed_bookings = Booking.objects.filter(
        customer=customer,
        status__in=['completed', 'cancelled']
    ).prefetch_related('jobcard_set__bill').order_by('-created_at')

    return render(request, 'customers/dashboard.html', {
        'customer': customer,
        'vehicles': vehicles,
        'active_bookings': active_bookings,
        'completed_bookings': completed_bookings
    })

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Vehicle

@login_required
def add_vehicle(request):
    if request.method == 'POST':
        customer = request.user.customer_profile

        Vehicle.objects.create(
            customer=customer,
            vehicle_number=request.POST['vehicle_number'],
            vehicle_type=request.POST['vehicle_type']
        )

        return redirect('customer_dashboard')

    return render(request, 'customers/add_vehicle.html')

from django.shortcuts import get_object_or_404
from billing.models import Bill
from django.utils import timezone
from django.contrib import messages

@login_required
def view_bill(request, booking_id):
    """View detailed bill for a booking"""
    from booking.models import Booking
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user.customer_profile)
    
    bill = Bill.objects.filter(jobcard__booking=booking).last()
    if not bill:
        messages.error(request, "Bill not generated yet for this booking.")
        return redirect('customer_dashboard')
        
    context = {
        'booking': booking,
        'bill': bill,
        'parts': bill.items.all()
    }
    return render(request, 'customers/view_bill.html', context)

@login_required
def pay_bill(request, bill_id):
    """Dummy payment module with card validation"""
    bill = Bill.objects.filter(id=bill_id, jobcard__booking__customer=request.user.customer_profile).last()
    if not bill:
        messages.error(request, "Bill not found.")
        return redirect('customer_dashboard')
    
    if request.method == 'POST':
        card_number = request.POST.get('card_number', '')
        expiry = request.POST.get('expiry', '')
        
        # 1. Capture last 4 digits
        clean_number = ''.join(filter(str.isdigit, card_number))
        last_4 = clean_number[-4:] if len(clean_number) >= 4 else "XXXX"
        
        # 2. Validate Expiry Date (MM / YY)
        try:
            from datetime import datetime
            expiry_clean = expiry.replace(' ', '')
            exp_month, exp_year = map(int, expiry_clean.split('/'))
            # Convert YY to YYYY
            exp_year += 2000
            
            now = datetime.now()
            if exp_year < now.year or (exp_year == now.year and exp_month < now.month):
                messages.error(request, "Payment Failed: Card has expired.")
                return redirect('pay_bill', bill_id=bill_id)
        except (ValueError, IndexError):
            messages.error(request, "Payment Failed: Invalid expiry date format.")
            return redirect('pay_bill', bill_id=bill_id)
        
        # 3. Process Successful "Dummy" Payment
        bill.is_paid = True
        bill.payment_method = f"Card (ending in {last_4})"
        bill.paid_at = timezone.now()
        bill.save()
        
        messages.success(request, f"Payment successful! Card ending in {last_4} was charged ₹{bill.total_amount}.")
        return redirect('view_bill', booking_id=bill.jobcard.booking.id)
        
    return render(request, 'customers/dummy_payment.html', {'bill': bill})
