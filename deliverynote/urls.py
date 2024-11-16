from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
# from .views import generate_pdf
urlpatterns = [
    path('', views.delivery_note, name='delivery_note'),
    path('delivery_note_details/<str:id>/', views.delivery_note_details, name='delivery_note_details'),
    path('delivery_note_delete/<str:id>/', views.delivery_note_delete, name='delivery_note_delete'),
    path('add_delivery_note_item/<str:id>/', views.add_delivery_note_item, name='add_delivery_note_item'),
     path('convert_invoice_to_delivery_note/<str:id>/', views.convert_invoice_to_delivery_note, name='convert-invoice-to-delivery-note'),
    path('generate_pdf_delivery_note/<str:id>/', views.generate_pdf_delivery_note, name='generate_pdf_delivery_note'),
    path('delivery_note_verification/<str:id>/', views.delivery_note_verification, name='delivery_note_verification'),

]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)