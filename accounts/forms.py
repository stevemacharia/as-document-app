from django import forms
from django.contrib.auth.models import User
# from user.models import PaymentOption
from accounts.models import BusinessAccount,PaymentOption
from django.contrib.auth.forms import UserCreationForm
from django.forms import ImageField

class BusinessAccountForm(forms.ModelForm):
    name = forms.CharField(max_length=255)
    email = forms.CharField(max_length=100)
    address = forms.CharField(max_length=255, label="Your P.O. Box address")
    location = forms.CharField(max_length=200, widget=forms.Textarea, label="Your physical location")
    phone_number = forms.CharField(max_length=100)
    tel = forms.CharField(max_length=100, label="Tel")
    logo = ImageField(required=True)

    class Meta:
        model = BusinessAccount
        fields = ['name', 'email', 'address', 'location', 'phone_number', 'tel', 'theme_color', 'logo']


        widgets = {
            'theme_color': forms.TextInput(attrs={
                'type': 'color',  # Bootstrap color picker
                'class': 'form-control form-control-color',  # Bootstrap 5 classes for styling
                'title': 'Choose your color',
                'label': 'select your primary color'
            }),
        }

    def clean_color(self):
        theme_color = self.cleaned_data['color']
        # Check if it's a valid hex color format
        if not theme_color.startswith('#') or len(theme_color) != 7:
            raise forms.ValidationError("Enter a valid color in hex format (e.g., #ff0000)")
        return theme_color
        
    # # Optional: You can also add custom form validation here if needed
    # def clean_image(self):
    #     image = self.cleaned_data.get('logo')
    #     if image:
    #         if image.size > 3 * 1024 * 1024:  # 3 MB limit
    #             raise forms.ValidationError("The image file is too large ( > 3MB )")
    #     return image

class PaymentOptionForm(forms.ModelForm):
    PAYMENT_OPTIONS = [
         ('', 'Select a payment method'),
        ('MM', 'Mobile Money Transfer'),
        ('BT', 'Bank Transfer'),
    ]
    name = forms.CharField(max_length=255)
    account_no = forms.CharField(max_length=100)
    payment_method = forms.ChoiceField(
        choices=PAYMENT_OPTIONS,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'payment-method'}),  # or forms.Select for a dropdown
        required=True
    )
    def clean_payment_method(self):
        payment_method = self.cleaned_data.get('payment_method')
        if payment_method == '':
            raise forms.ValidationError('Please select a valid payment method.')
        return payment_method
    class Meta:
        model = PaymentOption
        fields = ['payment_method', 'name', 'account_no']
