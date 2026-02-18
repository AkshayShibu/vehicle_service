from django.db import models
from mech.models import JobCard

class Bill(models.Model):
    jobcard = models.OneToOneField('mech.JobCard', on_delete=models.CASCADE)

    labour_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    parts_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Workflow tracking
    is_submitted_by_mechanic = models.BooleanField(default=False)
    is_approved_by_admin = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    # Payment tracking
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill for JobCard #{self.jobcard.id}"
    
    def calculate_total(self):
        """Calculate total bill amount"""
        self.total_amount = self.parts_total + self.labour_cost
        return self.total_amount



class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    jobcard = models.ForeignKey(JobCard, on_delete=models.CASCADE, null=True, blank=True)
    part_name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.part_name} (Bill #{self.bill.id})"

