from .models import Bill, BillItem
from mech.models import JobCard
from django.shortcuts import get_object_or_404, redirect

def add_part(request, jobcard_id):
    jobcard = get_object_or_404(JobCard, id=jobcard_id)

    bill, created = Bill.objects.get_or_create(jobcard=jobcard)

    if request.method == "POST":
        part_name = request.POST['part_name']
        quantity = int(request.POST['quantity'])
        unit_price = float(request.POST['unit_price'])

        item = BillItem.objects.create(
            bill=bill,
            part_name=part_name,
            quantity=quantity,
            unit_price=unit_price
        )

        # Update parts total
        bill.parts_total = sum(i.subtotal for i in bill.items.all())
        bill.total_amount = bill.parts_total + bill.labour_cost
        bill.save()

        return redirect('mechanic_dashboard')
