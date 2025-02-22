from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
# models.py
from django.db import models
from .utils import save_qr_code
from accounts.models import BusinessAccount
from django.core.exceptions import ValidationError
from PIL import Image
import uuid
import os


# Validator to check the file size
def validate_image_size(image):
    max_size = 3 * 1024 * 1024  # 3MB
    if image.size > max_size:
        raise ValidationError(f"The image size should not exceed 3 MB. Your file is {image.size / (1024 * 1024):.2f} MB")

# Function to rename the image file based on the 'name' column
def upload_to(instance, filename):
    extension = os.path.splitext(filename)[1]  # Get the file extension
    return f"item_images/{instance.name}{extension}"

# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    postal_address = models.CharField(max_length=400, null=True, blank=True)
    business_account = models.ForeignKey(BusinessAccount, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Clients"
        verbose_name_plural = 'Clients'


class Quotation(models.Model):
    STATUS_CHOICES = (
        (0, 'Draft'),
        (1, 'Final'),
    )
    quotation_id = models.CharField(blank=True, max_length=100)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    business_account = models.ForeignKey(BusinessAccount, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    quotation_doc = models.FileField(upload_to='quotation_docs', default='default.pdf', null=True, blank=True, max_length=500)
    data = models.CharField(max_length=255, blank=True, null=True)
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    note = models.CharField(null=True, blank=True, max_length=240)
    submission_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    taxable = models.BooleanField(default=True, null=True, blank=True)
    sub_total = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, default=0,  decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Automatically update total_price whenever subtotal is updated
        self.total_price = self.sub_total * Decimal('1.16')  # Assuming total_price is 1.16 times the subtotal
        super().save(*args, **kwargs)

class QuotationItems(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE)
    item = models.CharField(max_length=300)
    item_description = models.CharField(max_length=800)
    item_image = models.ImageField(upload_to="item_images/", blank=True, null=True, default="item_images/AS_LOGO.png")
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=15, decimal_places=2)


    def save(self):
        super().save()
        img = Image.open(self.item_image.path)
        if img.height > 600 or img.width > 600:
            output_size = (600, 600)
            img.thumbnail(output_size)
            img.save(self.item_image.path)

