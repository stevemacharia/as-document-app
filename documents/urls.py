from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('quotations', views.quotations, name='quotations'),
    path('quotation_details/<str:id>/', views.quotation_details, name='quotation_details'),
    path('quotation_delete/<str:id>/', views.quotation_delete, name='quotation_delete'),
    path('add_quotation_item/<str:id>/', views.add_quotation_item, name='add_quotation_item'),
    path('generate_pdf_quotation/<str:id>/', views.generate_pdf_quotation, name='generate_pdf_quotation'),
    path('clients', views.clients, name='clients'),
    path('client_details/<str:id>/', views.client_details, name='client_details'),
    path('client_delete/<str:id>/', views.client_delete, name='client_delete'),
    ############start of invoices###########
    # path('invoice_details/<str:id>/', views.invoice_details, name='invoice_details'),
    # path('invoice_delete/<str:id>/', views.invoice_delete, name='invoice_delete'),
    # path('add_ivoice_item/<str:id>/', views.add_invoice_item, name='add_invoice_item'),
    #############end of invoices##############
    path('generate_qr_code/', views.generate_qr_code, name='generate_qr_code'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)