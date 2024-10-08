from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
# from .views import generate_pdf

urlpatterns = [
    path('business-account-register/', views.busines_account_register, name='busines-account-register'),
    path('payment-account-register/', views.payment_account_register, name='payment-account-register'),
    path('client-address-creation/', views.client_account_creation, name='client-address-creation'),
    path('business-profile/<str:id>/', views.business_profile, name='business-profile'),
    path('', views.business_account, name='business-account'),
    path('business-account-dashbaord/<str:id>/', views.business_account_dashboard, name='business-account-dashboard'),
    path('business-account-delete/<str:id>/', views.business_account_deletion, name='business-account-deletion'),
]