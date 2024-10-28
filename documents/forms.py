from django import forms
from .models import Quotation, QuotationItems, Client
from crispy_bootstrap5.bootstrap5 import FloatingField
from django.contrib.admin.widgets import AdminDateWidget


class ClientForm(forms.ModelForm):
    name = forms.CharField()
    email = forms.EmailField(
        max_length=254, 
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email', 'class': 'form-control'})
    )
    phone_number = forms.CharField()
    postal_address = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Client
        fields = ['name', 'email', 'phone_number', 'postal_address']


class QuotationForm(forms.ModelForm):
    STATUS_CHOICES = (
        ('0', 'Draft'),
        ('1', 'Final'),
    )
    TAXABLE_CHOICES = (
        ('True', 'Yes'),
        ('False', 'No'),
    )


    client = forms.ModelChoiceField(queryset=Client.objects.all(), label="Choose client",
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    submission_date = forms.DateField(
        label="Submission Date",
        required=True,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
    )
    status = forms.ChoiceField(choices=STATUS_CHOICES, label='Status', required=True)
    taxable = forms.ChoiceField(
        choices=TAXABLE_CHOICES,
        label='Include 16% Tax',
        required=True
    )
    note = forms.CharField(required=False, label="Add a note to the Quotation", widget=forms.Textarea)
    class Meta:
        model = Quotation
        fields = ['client', 'submission_date', 'status', 'taxable', 'note']


class QuotationItemsForm(forms.ModelForm):
    item = forms.CharField(required=True, label="Item Name")
    item_description = forms.CharField(required=True, label="Description", widget=forms.Textarea)
    quantity = forms.IntegerField(required=True)
    price = forms.CharField(required=True, label="Unit cost")


    class Meta:
        model = QuotationItems
        fields = ['item', 'item_description', 'quantity', 'price']
