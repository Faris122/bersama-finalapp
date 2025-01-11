from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('services/', views.service_list, name='service_list'),
    path('services_map/', views.service_map, name='service_map'),
    path('service/<int:pk>/', views.service_detail, name='service_detail'),
]