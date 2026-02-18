from django.db import models
from customers.models import Customer

class Booking(models.Model):

    SERVICE_CHOICE = [
        ('general', 'General Service'),
        ('oil', 'Oil Change'),
        ('engine', 'Engine Work'),
        ('brake', 'Brake Service'),
        ('other', 'Other'),
    ]

    STATUS_CHOICE = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    service_type = models.CharField(
        max_length=20,
        choices=SERVICE_CHOICE
    )

    problem_description = models.TextField(
        blank=True,
        help_text="Customer can describe their problem here"
    )

    preferred_date = models.DateField()
    preferred_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking #{self.id}"
