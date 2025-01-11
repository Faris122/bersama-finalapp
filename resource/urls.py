from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('resources/', views.resource_list, name='resource_list'),
    path('resources/<int:pk>/', views.resource_detail, name='resource_detail'),
    path('resources/create/', views.create_resource, name='create_resource'),
]