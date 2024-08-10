from django import forms
from django.contrib.auth.models import User
from user.models import PaymentOption, UserProfile
from django.contrib.auth.forms import UserCreationForm


class UserProfileUpdateForm(forms.ModelForm):
    payment_option = forms.CharField(max_length=20)
    notes = forms.CharField(max_length=100)

    class Meta:
        model = UserProfile
        fields = ['payment_option', 'notes']