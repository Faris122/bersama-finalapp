from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('discussions/', views.discussion_list, name='discussion_list'),
    path('discussions/<int:pk>/', views.discussion_detail, name='discussion_detail'),
    path('discussions/create/', views.create_discussion, name='create_discussion'),

    path('api/discussions/', views.discussion_list_api, name='discussion_list_api'),
    path('api/discussions/create/', views.create_discussion_api, name='create_discussion_api'),
    path('api/discussions/<int:pk>/', views.discussion_detail_api, name='discussion_detail_api'),
    path('api/discussions/<int:pk>/add_comment/', views.add_comment_api, name='add_comment_api'),
    path('api/discussions/categories/', views.discussion_categories_list_api, name='discussion_categories_list_api'),
    
]