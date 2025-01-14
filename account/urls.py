from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    path('profile/', views.profile, name='profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    path('api/register/', views.register_user_api, name='register_api'),
    path('api/login/', views.login_user_api, name='login_api'),
    path('api/logout/', views.logout_user_api, name='logout_api'),

    path('api/profile/', views.profile_api, name='profile_api'),
    path('api/profile/<str:username>/', views.profile_api, name='profile_api'),
    path('api/edit_profile/',views.edit_profile_api,name='edit_profile_api')
]