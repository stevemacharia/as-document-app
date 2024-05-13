from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
import uuid


# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=400)
    postal_address = models.CharField(max_length=400)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Clients"
        verbose_name_plural = 'Clients'


class Quotation(models.Model):
    quotation_id = models.CharField(blank=True, max_length=100)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    status = models.BooleanField(default="False", null=True, blank=True)
    quotation_doc = models.FileField(upload_to='quotation_docs', default='default.pdf', null=True, blank=True)
    submission_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    sub_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.sub_total:
            self.total_price = self.sub_total * Decimal('1.16')  # Total price is 116% of sub total
        super().save(*args, **kwargs)

class QuotationItems(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE)
    item = models.CharField(max_length=300)
    item_description = models.CharField(max_length=800)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=15, decimal_places=2)


class Invoice(models.Model):
    invoice_id = models.CharField(blank=True, max_length=100)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    status = models.BooleanField(default="False", null=True, blank=True)
    quotation_doc = models.FileField(upload_to='quotation_docs', default='default.pdf', null=True, blank=True)
    submission_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


class InvoiceItems(models.Model):
    invoice = models.ForeignKey(Quotation, on_delete=models.CASCADE)
    item = models.CharField(max_length=300)
    item_description = models.CharField(max_length=800)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=15, decimal_places=2)