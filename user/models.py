from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class PaymentOption(models.Model):
    name = models.CharField(max_length=200, blank=True)
    account_number = models.CharField(max_length=200, blank=True)
    branch = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f'{self.name}'
    class Meta:
        verbose_name = "Payment Options"



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    payment_option = models.ForeignKey(PaymentOption, on_delete=models.CASCADE)
    notes = models.CharField(max_length=255, blank=True, null=True)
    

    def __str__(self):
        return f'{self.user.username}'

    class Meta:
        verbose_name = "User"