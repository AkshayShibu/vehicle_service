from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from billing.models import Bill, BillItem
from .models import JobCard, Mechanic

@login_required
def mechanic_dashboard(request):
    """Mechanic dashboard showing assigned jobs"""
    user = request.user

    # Safety check
    if not hasattr(user, 'mechanic_profile'):
        messages.error(request, "You are not authorized to access mechanic dashboard")
        return redirect('login')

    mechanic = user.mechanic_profile
    
    # Check if mechanic is approved
    if not mechanic.is_approved:
        messages.error(request, "Your account is pending admin approval")
        return redirect('login')

    # Get all jobs assigned to this mechanic
    active_jobs = JobCard.objects.filter(
        mechanic=user,
        booking__status__in=['approved', 'in_progress']
    ).select_related('booking__customer__user').order_by('-created_at')
    
    completed_jobs = JobCard.objects.filter(
        mechanic=user,
        booking__status='completed'
    ).select_related('booking__customer__user').order_by('-created_at')

    context = {
        'mechanic': mechanic,
        'active_jobs': active_jobs,
        'completed_jobs': completed_jobs,
    }

    return render(request, 'mech/dashboard.html', context)


@login_required
def job_details(request, jobcard_id):
    """View job details and manage billing"""
    jobcard = get_object_or_404(
        JobCard.objects.select_related('booking__customer__user', 'mechanic'),
        id=jobcard_id,
        mechanic=request.user
    )
    
    # Get or create bill for this jobcard
    bill, created = Bill.objects.get_or_create(jobcard=jobcard)
    
    # Get all parts added to this bill
    parts = BillItem.objects.filter(bill=bill)
    
    # Calculate parts total
    parts_total = sum(part.subtotal for part in parts)
    
    # Update bill parts total
    bill.parts_total = parts_total
    bill.save()
    
    # Calculate labour hours
    labour_hours = jobcard.get_labour_hours()
    
    context = {
        'jobcard': jobcard,
        'bill': bill,
        'parts': parts,
        'parts_total': parts_total,
        'labour_hours': labour_hours,
    }
    
    return render(request, 'mech/job_details.html', context)


@login_required
def start_work(request, jobcard_id):
    """Start work on a job"""
    jobcard = get_object_or_404(JobCard, id=jobcard_id, mechanic=request.user)
    
    if not jobcard.work_start_time:
        jobcard.work_start_time = timezone.now()
        jobcard.booking.status = 'in_progress'
        jobcard.booking.save()
        jobcard.save()
        messages.success(request, "Work started successfully!")
    else:
        messages.warning(request, "Work already started on this job")
    
    return redirect('job_details', jobcard_id=jobcard_id)


@login_required
def end_work(request, jobcard_id):
    """End work on a job"""
    jobcard = get_object_or_404(JobCard, id=jobcard_id, mechanic=request.user)
    
    if not jobcard.work_start_time:
        messages.error(request, "Please start work first")
        return redirect('job_details', jobcard_id=jobcard_id)
    
    if not jobcard.work_end_time:
        jobcard.work_end_time = timezone.now()
        jobcard.save()
        messages.success(request, "Work ended successfully!")
    else:
        messages.warning(request, "Work already ended on this job")
    
    return redirect('job_details', jobcard_id=jobcard_id)


@login_required
def add_part(request, jobcard_id):
    """Add parts to a job"""
    jobcard = get_object_or_404(JobCard, id=jobcard_id, mechanic=request.user)
    
    # Get or create bill
    bill, created = Bill.objects.get_or_create(jobcard=jobcard)

    if request.method == 'POST':
        part_name = request.POST.get('part_name')
        quantity = int(request.POST.get('quantity', 1))
        unit_price = float(request.POST.get('unit_price', 0))

        BillItem.objects.create(
            bill=bill,
            jobcard=jobcard,
            part_name=part_name,
            quantity=quantity,
            unit_price=unit_price
        )
        
        messages.success(request, f"Part '{part_name}' added successfully!")
        return redirect('job_details', jobcard_id=jobcard_id)

    return redirect('job_details', jobcard_id=jobcard_id)


@login_required
def delete_part(request, part_id):
    """Delete a part from bill"""
    part = get_object_or_404(BillItem, id=part_id)
    jobcard_id = part.jobcard.id
    
    # Verify mechanic owns this job
    if part.jobcard.mechanic == request.user:
        part.delete()
        messages.success(request, "Part deleted successfully!")
    else:
        messages.error(request, "Unauthorized action")
    
    return redirect('job_details', jobcard_id=jobcard_id)


@login_required
def submit_bill(request, jobcard_id):
    """Submit bill to admin for approval"""
    jobcard = get_object_or_404(JobCard, id=jobcard_id, mechanic=request.user)
    
    # Check if work is completed
    if not jobcard.work_start_time or not jobcard.work_end_time:
        messages.error(request, "Please complete work start and end times before submitting bill")
        return redirect('job_details', jobcard_id=jobcard_id)
    
    # Get or create bill
    bill, created = Bill.objects.get_or_create(jobcard=jobcard)
    
    # Calculate parts total
    parts = BillItem.objects.filter(bill=bill)
    parts_total = sum(part.subtotal for part in parts)
    
    bill.parts_total = parts_total
    bill.is_submitted_by_mechanic = True
    bill.submitted_at = timezone.now()
    bill.save()
    
    messages.success(request, "Bill submitted successfully! Waiting for admin approval.")
    return redirect('mechanic_dashboard')