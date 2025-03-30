from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # Page Views
    # Registration and Login
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    # API Views
    # Registrationa nd Login
    path('api/register/', views.register_user_api, name='register_api'),
    path('api/login/', views.login_user_api, name='login_api'),
    path('api/logout/', views.logout_user_api, name='logout_api'),

    # Profile
    path('api/profile/', views.profile_api, name='profile_api'),
    path('api/profile/<str:username>/', views.profile_api, name='profile_api'),
    path('api/edit_profile/',views.edit_profile_api,name='edit_profile_api'),

    # Address
    path('api/search-address/', views.search_address, name='search_address'),

    # Chat Functionality
    # Page Views
    path('chats/', views.chat_list, name='chat_list'),
    path('chat/<str:recipient_username>/', views.chat_view, name='chat'),

    # API Views
    path('api/chat/list/', views.chat_list_api, name='chat_list_api'),
    path('api/chat/<int:chat_id>/messages/', views.get_chat_messages_api, name='get_chat_messages'),
    path('api/chat/create_or_get/', views.create_or_get_chat_api, name='create_or_get_chat_api'),
    path('api/chat/unread_count/', views.total_unread_api, name='total_unread_api'),
]