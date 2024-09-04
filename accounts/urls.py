from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
# from .views import generate_pdf

urlpatterns = [
    path('business-profile/', views.profile, name='business-profile'),
    path('/', views.business_account, name='business-account'),
]