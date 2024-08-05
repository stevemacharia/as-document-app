from django import forms
from .models import Invoice, InvoiceItems, Client
from crispy_bootstrap5.bootstrap5 import FloatingField
from django.contrib.admin.widgets import AdminDateWidget


class InvoiceForm(forms.ModelForm):
    STATUS_CHOICES = (
        ('0', 'Draft'),
        ('1', 'Final'),
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
    class Meta:
        model = Invoice
        fields = ['client', 'submission_date', 'status']


class InvoiceItemsForm(forms.ModelForm):
    item = forms.CharField(required=True, label="Item Name")
    item_description = forms.CharField(required=True, label="Description", widget=forms.Textarea)
    quantity = forms.IntegerField(required=True)
    price = forms.CharField(required=True, label="Unit cost")
    unit = forms.CharField(required=True, label="Unit of Measurement")


    class Meta:
        model = InvoiceItems
        fields = ['item', 'item_description', 'quantity', 'price', 'unit']
