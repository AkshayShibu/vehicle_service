from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'service_type',
        'status',
        'preferred_date',
        'preferred_time',
        'created_at',
    )

    list_filter = ('status', 'service_type', 'preferred_date')
    search_fields = ('customer__vehicle_number', 'customer__name')
    ordering = ('-created_at',)
