from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
# from .views import generate_pdf
urlpatterns = [
    path('invoice', views.invoice, name='invoice'),
    path('invoice_details/<str:id>/', views.invoice_details, name='invoice_details'),
    path('invoice_delete/<str:id>/', views.invoice_delete, name='invoice_delete'),
    path('add_invoice_item/<str:id>/', views.add_invoice_item, name='add_invoice_item'),
    path('generate_pdf_invoice/<str:id>/', views.generate_pdf_invoice, name='generate_pdf_invoice'),
    path('invoice_verification/<str:id>/', views.invoice_verification, name='invoice_verification'),

]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)