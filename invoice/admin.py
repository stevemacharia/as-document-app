from django.contrib import admin
from .models import Invoice, InvoiceItems

# Register your models here.
class InvoiceItemsAdmin(admin.StackedInline):
    model = InvoiceItems


# this class define which department columns will be shown in the department admin web site.
class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceItemsAdmin]
    # a list of displayed columns name.
    list_display = ['invoice_id', 'client', 'total_price', 'submission_date', 'status']
    # list_filter = ('p',)
    # define search columns list, then a search box will be added at the top of Department list page.
    search_fields = ['invoice_id', 'client', ]
    # define model data list ordering.
    ordering = ('created_at',)


admin.site.register(Invoice, InvoiceAdmin)