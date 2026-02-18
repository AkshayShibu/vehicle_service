from django.db import models
from django.contrib.auth.models import User
from booking.models import Booking
# Create your models here.
class JobCard(models.Model):
    booking = models.ForeignKey('booking.Booking', on_delete=models.CASCADE)
    mechanic = models.ForeignKey(User, on_delete=models.CASCADE)

    work_start_time = models.DateTimeField(null=True, blank=True)
    work_end_time = models.DateTimeField(null=True, blank=True)

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"JobCard - {self.booking.id}"
    
    def get_labour_hours(self):
        """Calculate total labour hours"""
        if self.work_start_time and self.work_end_time:
            delta = self.work_end_time - self.work_start_time
            return round(delta.total_seconds() / 3600, 2)
        return 0

    


class Mechanic(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='mechanic_profile'
    )
    phone = models.CharField(max_length=15)
    experience = models.PositiveIntegerField(help_text="Years of experience")
    
    # Approval fields
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_mechanics'
    )

    def __str__(self):
        return self.user.username

