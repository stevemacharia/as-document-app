from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
# models.py
from django.db import models
from .utils import save_qr_code
from PIL import Image
import uuid
from documents.models import Client
from accounts.models import BusinessAccount, PaymentOption
from django.core.exceptions import ObjectDoesNotExist


# Create your models here.
def get_default_payment_option_account():
    try:
        # Return the ID of the first BusinessAccount, or another specific ID
        return PaymentOption.objects.first().id
    except (ObjectDoesNotExist, AttributeError):
        # Handle case where no BusinessAccount exists yet
        return None  # Or handle with a custom fallback if needed



class DeliveryNote(models.Model):
    STATUS_CHOICES = (
        (0, 'Draft'),
        (1, 'Final'),
    )
    PAYMENT_STATUS_CHOICES = (
        (0, 'Unpaid'),
        (1, 'Paid'),
    )
    dnote_id = models.CharField(blank=True, max_length=100)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='delivery_note_client')
    business_account = models.ForeignKey(BusinessAccount, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    payment_account = models.ForeignKey(PaymentOption, on_delete=models.CASCADE, default= get_default_payment_option_account
    )
    payment_status = models.IntegerField(choices=PAYMENT_STATUS_CHOICES, default=0)
    dnote_doc = models.FileField(upload_to='delivery_note_docs', default='default.pdf', null=True, blank=True, max_length=500)
    data = models.CharField(max_length=255, blank=True, null=True)
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    note = models.CharField(null=True, blank=True, max_length=700)
    submission_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    # taxable = models.BooleanField(default=True, null=True, blank=True)
    # sub_total = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True, blank=True)
    # total_price = models.DecimalField(max_digits=10, default=0,  decimal_places=2, blank=True, null=True)

    # def save(self, *args, **kwargs):
    #     # Automatically update total_price whenever subtotal is updated
    #     self.total_price = self.sub_total * Decimal('1.16')  # Assuming total_price is 1.16 times the subtotal
    #     super().save(*args, **kwargs)

class DeliveryNoteItems(models.Model):
    dnote = models.ForeignKey(DeliveryNote, on_delete=models.CASCADE)
    item = models.CharField(max_length=300)
    item_description = models.CharField(max_length=800)
    quantity = models.IntegerField()
    # price = models.DecimalField(max_digits=15, decimal_places=2)





