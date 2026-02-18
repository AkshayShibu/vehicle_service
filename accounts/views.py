from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from customers.models import Customer
from mech.models import Mechanic


# cust register
from customers.models import Customer, Vehicle

def customer_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        phone = request.POST['phone']
        vehicle_number = request.POST['vehicle_number']
        vehicle_type = request.POST['vehicle_type']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('customer_register')

        # create auth user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # create customer profile
        customer = Customer.objects.create(
            user=user,
            name=username,
            phone=phone,
            email=email
        )

        # create vehicle
        Vehicle.objects.create(
            customer=customer,
            vehicle_number=vehicle_number,
            vehicle_type=vehicle_type
        )

        messages.success(request, "Customer registered successfully. Please login.")
        return redirect('login')

    return render(request, 'accounts/customer_register.html')

#mech register
def mechanic_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        experience = request.POST['experience']
        password = request.POST['password']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.is_active = False   # admin approval required
        user.is_staff = False
        user.save()

        Mechanic.objects.create(
            user=user,
            phone=phone,
            experience=experience
        )

        return redirect('login')

    return render(request, 'accounts/mechanic_register.html')
#login
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, "Account not approved by admin.")
                return redirect('login')

            login(request, user)

            # Redirect admin/superuser to custom admin dashboard
            if user.is_superuser or user.is_staff:
                # Check if user is a mechanic
                if hasattr(user, 'mechanic_profile'):
                    return redirect('mechanic_dashboard')
                else:
                    # Admin user - redirect to custom admin dashboard
                    return redirect('admin_dashboard')
            else:
                # Regular customer
                return redirect('customer_dashboard')

        messages.error(request, "Invalid username or password")

    return render(request, 'accounts/login.html')



#logout
def logout_view(request):
    logout(request)
    return redirect('login')

#homepage
def homepage(request):
    return render(request, 'accounts/homepage.html')