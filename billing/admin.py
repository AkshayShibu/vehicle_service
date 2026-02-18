from django.contrib import admin
from .models import Bill, BillItem


class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 1


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    inlines = [BillItemInline]
    list_display = ('id', 'jobcard', 'labour_cost', 'total_amount', 'created_at')


