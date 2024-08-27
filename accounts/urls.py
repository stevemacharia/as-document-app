from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
# from .views import generate_pdf

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('business-accounts/', views.business_account, name='business-account'),
]