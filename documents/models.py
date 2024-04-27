from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
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
    quotation_id = models.CharField(primary_key=True, default=uuid.uuid4, blank=True, editable=False,
                                    max_length=100)
    customer_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.BooleanField(default="False", null=True, blank=True)
    quotation_doc = models.FileField(upload_to='quotation', default='default.jpg', null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)


class QuotationItems(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE)
    item = models.CharField(max_length=100)
    item_description = models.CharField(max_length=500)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=15, decimal_places=2)
