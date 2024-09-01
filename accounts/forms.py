from django import forms
from django.contrib.auth.models import User
from user.models import PaymentOption
from accounts.models import BusinessAccount
from django.contrib.auth.forms import UserCreationForm


class BusinessAccountForm(forms.ModelForm):
    name = forms.CharField(max_length=255)
    address = forms.CharField(max_length=255, label="Your P.O. Box address")
    email = forms.CharField(max_length=100)
    location = forms.CharField(max_length=200, widget=forms.Textarea, label="Your physical location")
    phone_number = forms.CharField(max_length=100)

    class Meta:
        model = BusinessAccount
        fields = ['name', 'address', 'email', 'location', 'phone_number']