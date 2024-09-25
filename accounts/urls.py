from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
# from .views import generate_pdf

urlpatterns = [
    path('business-profile/<str:id>/', views.business_profile, name='business-profile'),
    path('', views.business_account, name='business-account'),
    path('business-account-dashbaord/<str:id>/', views.business_account_dashboard, name='business-account-dashboard'),
    path('business-account-delete/<str:id>/', views.business_account_deletion, name='business-account-deletion'),
]