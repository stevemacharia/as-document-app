from django import forms
from .models import Quotation, QuotationItems, Client


class QuotationForm(forms.ModelForm):
    quotation_id = forms.CharField()
    customer_id = forms.CharField()