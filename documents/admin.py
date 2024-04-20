from django.contrib import admin
# Register your models here.
from .models import Client, Quotation, QuotationItems


# Register your models here.


class QuotationItemsAdmin(admin.StackedInline):
    model = QuotationItems


# this class define which department columns will be shown in the department admin web site.
class QuotationAdmin(admin.ModelAdmin):
    inlines = [QuotationItemsAdmin]
    # a list of displayed columns name.
    list_display = ['quotation_id', 'customer_id', 'amount', 'date', 'status', 'date']
    # list_filter = ('p',)
    # define search columns list, then a search box will be added at the top of Department list page.
    search_fields = ['quotation_id', 'customer_id', ]
    # define model data list ordering.
    ordering = ('date',)


admin.site.register(Quotation, QuotationAdmin)
