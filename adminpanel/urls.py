from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.users_list, name='users_list'),
    path('mechanics/pending/', views.pending_mechanics, name='pending_mechanics'),
    path('mechanics/approve/<int:mechanic_id>/', views.approve_mechanic, name='approve_mechanic'),
    path('mechanics/reject/<int:mechanic_id>/', views.reject_mechanic, name='reject_mechanic'),
    path('bookings/', views.bookings_list, name='bookings_list'),
    path('bookings/approve/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('assign-job/', views.assign_job, name='assign_job'),
    path('bills/pending/', views.pending_bills, name='pending_bills'),
    path('bills/review/<int:bill_id>/', views.review_bill, name='review_bill'),
    path('bills/approved/', views.approved_bills, name='approved_bills'),
]
