from django.contrib import admin
from .models import Receipt, ReceiptItems

# Register your models here.
class ReceiptItemsAdmin(admin.StackedInline):
    model = ReceiptItems


# this class define which department columns will be shown in the department admin web site.
class ReceiptAdmin(admin.ModelAdmin):
    inlines = [ReceiptItemsAdmin]
    # a list of displayed columns name.
    list_display = ['receipt_id', 'client', 'total_price', 'submission_date', 'status']
    # list_filter = ('p',)
    # define search columns list, then a search box will be added at the top of Department list page.
    search_fields = ['receipt_id', 'client', ]
    # define model data list ordering.
    ordering = ('created_at',)


admin.site.register(Receipt, ReceiptAdmin)