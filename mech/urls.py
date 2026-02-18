from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.mechanic_dashboard, name='mechanic_dashboard'),
    path('job/<int:jobcard_id>/', views.job_details, name='job_details'),
    path('job/<int:jobcard_id>/start/', views.start_work, name='start_work'),
    path('job/<int:jobcard_id>/end/', views.end_work, name='end_work'),
    path('job/<int:jobcard_id>/add-part/', views.add_part, name='add_part'),
    path('part/<int:part_id>/delete/', views.delete_part, name='delete_part'),
    path('job/<int:jobcard_id>/submit-bill/', views.submit_bill, name='submit_bill'),
]
