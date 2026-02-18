from django.urls import path
from . import views
from booking import views as booking_views

urlpatterns = [
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('add-vehicle/', views.add_vehicle, name='add_vehicle'),
    path('bill/<int:booking_id>/', views.view_bill, name='view_bill'),
    path('bill/pay/<int:bill_id>/', views.pay_bill, name='pay_bill'),
    path('booking/create/', booking_views.create_booking, name='create_booking'),
    path('booking/cancel/<int:booking_id>/', booking_views.cancel_booking, name='cancel_booking'),
]
