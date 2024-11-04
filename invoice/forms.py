from django import forms
from .models import Invoice, InvoiceItems
from crispy_bootstrap5.bootstrap5 import FloatingField
from django.contrib.admin.widgets import AdminDateWidget
from accounts.models import BusinessAccount, PaymentOption
from documents.models import Client

class InvoiceForm(forms.ModelForm):
    STATUS_CHOICES = (
        ('0', 'Draft'),
        ('1', 'Complete'),
    )
    PAYMENT_STATUS_CHOICES = (
        ('0', 'Unpaid'),
        ('1', 'Paid'),
    )
    TAXABLE_CHOICES = (
        ('True', 'Yes'),
        ('False', 'No'),
    )

    client = forms.ModelChoiceField(
        queryset=Client.objects.none(),
        label="Choose client",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    payment_account = forms.ModelChoiceField(
        queryset=PaymentOption.objects.none(),
        label="Choose payment account",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    payment_status = forms.ChoiceField(choices=PAYMENT_STATUS_CHOICES, label='Payment status', required=True)

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
    note = forms.CharField(required=False, label="Add a note to the Invoice", widget=forms.Textarea)
    class Meta:
        model = Invoice
        fields = ['client', 'payment_account', 'payment_status', 'submission_date', 'taxable', 'note', 'status']

    def set_request(self, request):
        self.request = request
        business_account_id = request.session.get('selected_business_account')
        
        if business_account_id:
            try:
                selected_business_account = BusinessAccount.objects.get(id=business_account_id)

                # If editing an instance, include the current client and payment_account
                if self.instance.pk:
                    self.fields['client'].queryset = Client.objects.filter(
                        business_account=selected_business_account
                    ) | Client.objects.filter(id=self.instance.client.id)

                    self.fields['payment_account'].queryset = PaymentOption.objects.filter(
                        business=selected_business_account
                    ) | PaymentOption.objects.filter(id=self.instance.payment_account.id)
                else:
                    # For new forms, filter only by business account
                    self.fields['client'].queryset = Client.objects.filter(business_account=selected_business_account)
                    self.fields['payment_account'].queryset = PaymentOption.objects.filter(business=selected_business_account)
                    
            except BusinessAccount.DoesNotExist:
                self.fields['client'].queryset = Client.objects.none()
                self.fields['payment_account'].queryset = PaymentOption.objects.none()

class InvoiceItemsForm(forms.ModelForm):
    item = forms.CharField(required=True, label="Item Name")
    item_description = forms.CharField(required=True, label="Description", widget=forms.Textarea)
    quantity = forms.IntegerField(required=True)
    price = forms.CharField(required=True, label="Unit cost")
    # unit = forms.CharField(required=True, label="Unit of Measurement")


    class Meta:
        model = InvoiceItems
        fields = ['item', 'item_description', 'quantity', 'price']
