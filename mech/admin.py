from django.contrib import admin
from .models import JobCard
# Register your models here.
@admin.register(JobCard)
class JobCardAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'mechanic', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('booking__id', 'mechanic__username')