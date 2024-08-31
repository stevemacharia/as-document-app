from django.contrib import admin
from .models import BusinessAccount

# Register your models here.
class BusinessAccountAdmin(admin.ModelAdmin):
    model = BusinessAccount
    list_display = ['user', 'name', 'email', 'address', 'location', 'phone_number']
    search_fields = ['name']

admin.site.register( BusinessAccount, BusinessAccountAdmin)