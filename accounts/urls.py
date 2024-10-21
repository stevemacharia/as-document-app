from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
# from .views import generate_pdf

urlpatterns = [
    path('business-account-register/', views.busines_account_register, name='busines-account-register'),
    path('payment-account-register/', views.payment_account_register, name='payment-account-register'),
    path('payment-account-add', views.payment_account_add, name='payment-account-add'),
    path('payment-account-delete/<str:id>/', views.payment_account_delete, name='payment-account-delete'),
    path('payment-edit/<str:id>/', views.payment_edit, name='payment-edit'),
    path('client-edit/<str:id>/', views.client_edit, name='client-edit'),
    path('client-profile-add', views.client_profile_add, name='client-profile-add'),
    path('client-profile-delete/<str:id>/', views.client_profile_delete, name='client-profile-delete'),
    path('client-address-creation/', views.client_account_creation, name='client-address-creation'),
    path('business-profile', views.business_profile, name='business-profile'),
    path('', views.business_account, name='business-account'),
    path('business-account-dashbaord/<str:id>/', views.business_account_dashboard, name='business-account-dashboard'),
    path('business-account-delete/<str:id>/', views.business_account_deletion, name='business-account-deletion'),
]