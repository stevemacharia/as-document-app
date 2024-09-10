from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from PIL import Image
import os

# Create your models here.
# Validator to check the file size
def validate_image_size(image):
    max_size = 3 * 1024 * 1024  # 3MB
    if image.size > max_size:
        raise ValidationError(f"The image size should not exceed 3 MB. Your file is {image.size / (1024 * 1024):.2f} MB")

# Function to rename the image file based on the 'name' column
def upload_to(instance, filename):
    extension = os.path.splitext(filename)[1]  # Get the file extension
    return f"business_logos/{instance.name}{extension}"

class BusinessAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, blank=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    tel = models.CharField(max_length=100, blank=True, null=True)
    theme_color = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(upload_to="business_logos/",  blank=True, null=True, default='AS_LOGO.png')
    # payment_option = models.ForeignKey(PaymentOption, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Business Accounts"

    def save(self):
        super().save()

        img = Image.open(self.logo.path)

        if img.height > 600 or img.width > 600:
            output_size = (600, 600)
            img.thumbnail(output_size)
            img.save(self.logo.path)