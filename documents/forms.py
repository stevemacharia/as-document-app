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
        ('1', 'Final'),
        ('0', 'Draft'),
    )


    client = forms.ModelChoiceField(queryset=Client.objects.all(), label="Choose client",
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    submission_date = forms.DateField(
        label="Submission Date",
        required=True,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
    )

    class Meta:
        model = Quotation
        fields = ['client', 'submission_date']


class QuotationItemsForm(forms.ModelForm):
    item = forms.CharField()
    item_description = forms.CharField(required=False, widget=forms.Textarea)
    quantity = forms.IntegerField(required=False)
    price = forms.CharField()

    class Meta:
        model = QuotationItems
        fields = ['item', 'item_description', 'quantity', 'price']
