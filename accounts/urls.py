from django.urls import path
from . import views

urlpatterns = [
    path('register/customer/', views.customer_register, name='customer_register'),
    path('register/mechanic/', views.mechanic_register, name='mechanic_register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/mechanic/', views.mechanic_register, name='mechanic_register'),
]
