from django import forms
from django.contrib.auth.models import User
from customers.models import Customer

class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=False)

    class Meta:
        model = Customer
        fields = ['phone', 'vehicle_number', 'vehicle_type']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data.get('email')
        )

        customer = super().save(commit=False)
        customer.user = user

        if commit:
            customer.save()
        return customer
