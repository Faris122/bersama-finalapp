from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # Page View
    path('discussions/', views.discussion_list, name='discussion_list'),
    path('discussions/<int:pk>/', views.discussion_detail, name='discussion_detail'),
    path('discussions/create/', views.create_discussion, name='create_discussion'),

    # API View
    path('api/discussions/', views.discussion_list_api, name='discussion_list_api'),
    path('api/discussions/create/', views.create_discussion_api, name='create_discussion_api'),
    path('api/discussions/<int:pk>/', views.discussion_detail_api, name='discussion_detail_api'),
    path('api/discussions/<int:pk>/add_comment/', views.add_comment_api, name='add_comment_api'),
    path('api/discussions/comments/<int:comment_id>/delete/', views.delete_comment_api, name='delete_comment_api'),
    path('api/discussions/categories/', views.discussion_categories_list_api, name='discussion_categories_list_api'),
    path('api/discussions/search/',views.search_discussions, name='search_discussions'),
    path('api/discussions/posted_by/<str:username>/',views.discussions_posted_by, name='discussions_posted_by'),
    path('api/discussions/commented_by/<str:username>/',views.discussions_commented_by, name='discussions_commented_by'),
    path('api/discussions/<int:pk>/delete/', views.delete_discussion_api, name='delete_discussion_api')
    
]