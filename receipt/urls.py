from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
# from .views import generate_pdf
urlpatterns = [
    path('receipt', views.receipt, name='receipt'),
    path('receipt_details/<str:id>/', views.receipt_details, name='receipt_details'),
    path('receipt_delete/<str:id>/', views.receipt_delete, name='receipt_delete'),
    path('add_receipt_item/<str:id>/', views.add_receipt_item, name='add_receipt_item'),
    path('convert_invoice_to_receipt/<str:id>/', views.convert_invoice_to_receipt, name='convert-invoice-to-receipt'),
    path('generate_pdf_receipt/<str:id>/', views.generate_pdf_receipt, name='generate_pdf_receipt'),
    path('receipt_verification/<str:id>/', views.receipt_verification, name='receipt_verification'),

]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)