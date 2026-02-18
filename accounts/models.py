from django.db import models
from django.contrib.auth.models import User

# class Customer(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     phone = models.CharField(max_length=15, blank=True)

#     def __str__(self):
#         return self.user.username


# class Vehicle(models.Model):
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
#     vehicle_number = models.CharField(max_length=20)
#     vehicle_type = models.CharField(max_length=20)

#     def __str__(self):
#         return f"{self.vehicle_number} - {self.customer.user.username}"
