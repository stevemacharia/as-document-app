from django.contrib import admin
from deliverynote.models import DeliveryNote

# Register your models here.
# Register your models here.
class DeliveryNoteAdmin(admin.ModelAdmin):
    model = DeliveryNote


admin.site.register(DeliveryNote, DeliveryNoteAdmin)