from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('discussions/', views.discussion_list, name='discussion_list'),
    path('discussions/<int:pk>/', views.discussion_detail, name='discussion_detail'),
    path('discussions/create/', views.create_discussion, name='create_discussion'),
    
]