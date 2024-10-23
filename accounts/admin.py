from django.contrib import admin
from .models import BusinessAccount, PaymentOption

# Register your models here.
class PaymentOptionAdmin(admin.StackedInline):
    model = PaymentOption

class BusinessAccountAdmin(admin.ModelAdmin):
    inlines = [PaymentOptionAdmin]
    # model = BusinessAccount
    list_display = ['user', 'name', 'email', 'address', 'location', 'phone_number']
    search_fields = ['name']

admin.site.register( BusinessAccount, BusinessAccountAdmin)