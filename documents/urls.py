from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('quotations', views.quotations, name='quotations'),
    path('clients', views.clients, name='clients'),
    path('client_details/<str:id>/', views.client_details, name='client_details'),
    path('client_delete/<str:id>/', views.client_delete, name='client_delete'),
]
