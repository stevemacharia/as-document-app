from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    postal_address = models.CharField(max_length=100)


class Quotation(models.Model):
    quotation_id = models.CharField(max_length=100, blank=False, primary_key=True)
    customer_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.BooleanField(default="False", null=True, blank=True)
    quotation_doc = models.FileField(upload_to='quotation', default='default.jpg')
    date = models.DateTimeField(default=timezone.now)


class QuotationItems(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE)
    item = models.CharField(max_length=100)
    item_description = models.CharField(max_length=500)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=15, decimal_places=2)
