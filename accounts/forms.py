from django import forms
from django.contrib.auth.models import User
from user.models import PaymentOption, Account
from django.contrib.auth.forms import UserCreationForm


class AccountForm(forms.ModelForm):
    business_name = forms.CharField(max_length=20)
    address = forms.CharField(max_length=100)
    email = forms.CharField(max_length=100)
    # phone_number = forms.CharField(max_length=100)

    class Meta:
        model = Account
        fields = ['business_name', 'address', 'email']