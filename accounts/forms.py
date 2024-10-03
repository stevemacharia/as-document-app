from django import forms
from django.contrib.auth.models import User
from user.models import PaymentOption
from accounts.models import BusinessAccount
from django.contrib.auth.forms import UserCreationForm
from django.forms import ImageField

class BusinessAccountForm(forms.ModelForm):
    name = forms.CharField(max_length=255)
    email = forms.CharField(max_length=100)
    address = forms.CharField(max_length=255, label="Your P.O. Box address")
    location = forms.CharField(max_length=200, widget=forms.Textarea, label="Your physical location")
    phone_number = forms.CharField(max_length=100)
    tel = forms.CharField(max_length=100, label="Tel")
    # logo = ImageField()

    class Meta:
        model = BusinessAccount
        fields = ['name', 'email', 'address', 'location', 'phone_number', 'tel', 'theme_color']


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