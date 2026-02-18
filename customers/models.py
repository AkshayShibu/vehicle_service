from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer_profile'
    )
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username


class Vehicle(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='vehicles'
    )
    vehicle_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.vehicle_number}"
