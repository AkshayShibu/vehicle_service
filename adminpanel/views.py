from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from booking.models import Booking
from mech.models import JobCard, Mechanic
from billing.models import Bill, BillItem
from customers.models import Customer


def is_admin(user):
    """Check if user is admin/staff"""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Main admin dashboard with statistics"""
    # Get statistics
    total_users = User.objects.count()
    total_customers = Customer.objects.count()
    pending_mechanics = Mechanic.objects.filter(is_approved=False).count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    pending_bills = Bill.objects.filter(
        is_submitted_by_mechanic=True,
        is_approved_by_admin=False
    ).count()
    
    # Recent bookings
    recent_bookings = Booking.objects.all().order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_customers': total_customers,
        'pending_mechanics': pending_mechanics,
        'pending_bookings': pending_bookings,
        'pending_bills': pending_bills,
        'recent_bookings': recent_bookings,
    }
    
    return render(request, 'adminpanel/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def users_list(request):
    """Display all registered users"""
    users = User.objects.all().order_by('-date_joined')
    total_count = users.count()
    
    context = {
        'users': users,
        'total_count': total_count,
    }
    
    return render(request, 'adminpanel/users_list.html', context)


@login_required
@user_passes_test(is_admin)
def pending_mechanics(request):
    """Show mechanics awaiting approval"""
    pending = Mechanic.objects.filter(is_approved=False).select_related('user')
    approved = Mechanic.objects.filter(is_approved=True).select_related('user')
    
    context = {
        'pending_mechanics': pending,
        'approved_mechanics': approved,
    }
    
    return render(request, 'adminpanel/pending_mechanics.html', context)


@login_required
@user_passes_test(is_admin)
def approve_mechanic(request, mechanic_id):
    """Approve a mechanic"""
    mechanic = get_object_or_404(Mechanic, id=mechanic_id)
    
    mechanic.is_approved = True
    mechanic.approved_at = timezone.now()
    mechanic.approved_by = request.user
    mechanic.save()
    
    return redirect('pending_mechanics')


@login_required
@user_passes_test(is_admin)
def reject_mechanic(request, mechanic_id):
    """Reject/delete a mechanic application"""
    mechanic = get_object_or_404(Mechanic, id=mechanic_id)
    mechanic.delete()
    
    return redirect('pending_mechanics')


@login_required
@user_passes_test(is_admin)
def bookings_list(request):
    """Display all booking requests"""
    # Filter bookings by status
    status_filter = request.GET.get('status', 'all')
    
    if status_filter == 'all':
        bookings = Booking.objects.all()
    else:
        bookings = Booking.objects.filter(status=status_filter)
    
    bookings = bookings.select_related('customer__user').order_by('-created_at')
    
    # Get approved mechanics for assignment
    mechanics = Mechanic.objects.filter(is_approved=True).select_related('user')
    
    context = {
        'bookings': bookings,
        'mechanics': mechanics,
        'status_filter': status_filter,
    }
    
    return render(request, 'adminpanel/bookings_list.html', context)


@login_required
@user_passes_test(is_admin)
def approve_booking(request, booking_id):
    """Approve a booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'approved'
    booking.save()
    
    return redirect('bookings_list')


@login_required
@user_passes_test(is_admin)
def assign_job(request):
    """Assign booking to mechanic (reusing existing view with improvements)"""
    # Exclude bookings that already have a job card
    bookings = Booking.objects.filter(
        status__in=['pending', 'approved']
    ).exclude(jobcard__isnull=False)
    mechanics = Mechanic.objects.filter(is_approved=True).select_related('user')

    if request.method == "POST":
        booking_id = request.POST.get('booking_id')
        mechanic_id = request.POST.get('mechanic_id')
        
        booking = get_object_or_404(Booking, id=booking_id)
        mechanic_user = get_object_or_404(User, id=mechanic_id)

        # Prevent duplicate job cards for same booking
        if JobCard.objects.filter(booking=booking).exists():
            messages.warning(request, f"A JobCard already exists for Booking #{booking_id}")
            return redirect('assign_job')

        # Create job card
        JobCard.objects.create(
            booking=booking,
            mechanic=mechanic_user
        )
        
        # Update booking status
        booking.status = 'in_progress'
        booking.save()

        return redirect('assign_job')

    return render(request, 'adminpanel/assign_job.html', {
        'bookings': bookings,
        'mechanics': mechanics
    })


@login_required
@user_passes_test(is_admin)
def pending_bills(request):
    """Show bills submitted by mechanics awaiting admin approval"""
    bills = Bill.objects.filter(
        is_submitted_by_mechanic=True,
        is_approved_by_admin=False
    ).select_related('jobcard__booking__customer__user', 'jobcard__mechanic')
    
    context = {
        'bills': bills,
    }
    
    return render(request, 'adminpanel/pending_bills.html', context)


@login_required
@user_passes_test(is_admin)
def review_bill(request, bill_id):
    """Admin reviews bill and adds labour cost"""
    bill = get_object_or_404(
        Bill.objects.select_related('jobcard__booking__customer__user', 'jobcard__mechanic'),
        id=bill_id
    )
    
    # Get bill items
    bill_items = bill.items.all()
    
    # Calculate parts total
    parts_total = sum(item.subtotal for item in bill_items)
    
    # Get labour hours
    labour_hours = bill.jobcard.get_labour_hours()
    
    if request.method == 'POST':
        labour_cost = request.POST.get('labour_cost')
        
        # Convert to Decimal
        from decimal import Decimal
        bill.labour_cost = Decimal(labour_cost)
        bill.parts_total = parts_total
        bill.calculate_total()
        bill.is_approved_by_admin = True
        bill.approved_at = timezone.now()
        bill.save()
        
        # Update booking status to completed
        bill.jobcard.booking.status = 'completed'
        bill.jobcard.booking.save()
        
        return redirect('pending_bills')
    
    context = {
        'bill': bill,
        'bill_items': bill_items,
        'parts_total': parts_total,
        'labour_hours': labour_hours,
    }
    
    return render(request, 'adminpanel/review_bill.html', context)

@login_required
@user_passes_test(is_admin)
def approved_bills(request):
    """View to list all approved bills and their payment status"""
    status_filter = request.GET.get('status', 'all')
    
    bills = Bill.objects.filter(is_approved_by_admin=True).select_related(
        'jobcard__booking__customer__user', 
        'jobcard__mechanic'
    ).order_by('-approved_at')
    
    if status_filter == 'paid':
        bills = bills.filter(is_paid=True)
    elif status_filter == 'unpaid':
        bills = bills.filter(is_paid=False)
        
    context = {
        'bills': bills,
        'status_filter': status_filter
    }
    return render(request, 'adminpanel/approved_bills.html', context)
