from django import forms
from .models import Quotation, QuotationItems, Client
from crispy_bootstrap5.bootstrap5 import FloatingField
from django.contrib.admin.widgets import AdminDateWidget


class ClientForm(forms.ModelForm):
    name = forms.CharField()
    address = forms.CharField()
    postal_address = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Client
        fields = ['name', 'address', 'postal_address']


class QuotationForm(forms.ModelForm):
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
        model = Quotation
        fields = ['client', 'submission_date', 'status']


class QuotationItemsForm(forms.ModelForm):
    item = forms.CharField(required=True, label="Item Name")
    item_description = forms.CharField(required=True, label="Description", widget=forms.Textarea)
    quantity = forms.IntegerField(required=True)
    price = forms.CharField(required=True, label="Unit cost")


    class Meta:
        model = QuotationItems
        fields = ['item', 'item_description', 'quantity', 'price']
