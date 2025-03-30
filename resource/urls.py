from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # Page View
    path('resources/', views.resource_list, name='resource_list'),
    path('bursaries/', views.bursary_list, name='bursary_list'),
    path('resources/<int:pk>/', views.resource_detail, name='resource_detail'),
    path('resources/create/', views.create_resource, name='create_resource'),

    # API Views
    path('api/resources/', views.resource_list_api, name='resource_list_api'),
    path('api/bursaries/', views.bursary_list_api, name='bursary_list_api'),
    path('api/resources/create/', views.create_resource_api, name='create_resource_api'),
    path('api/resources/create/bursary/', views.create_bursary_api, name='create_bursary_api'),
    path('api/resources/<int:pk>/', views.resource_detail_api, name='resource_detail_api'),
    path('api/resources/<int:pk>/delete/', views.delete_resource_api, name='delete_resource_api'),
    path('api/resources/<int:pk>/add_comment/', views.add_comment_api, name='add_comment_api'),
    path('api/resources/comments/<int:comment_id>/delete/', views.delete_comment_api, name='delete_comment_api'),
    path('api/resources/categories/', views.resource_categories_list_api, name='resource_categories_list_api'),
    path('api/resources/search/',views.search_resources, name='search_resources'),
    path('api/bursaries/search/',views.search_bursaries, name='search_bursaries'),
    path('api/bursaries/levels/', views.get_bursary_levels, name='get_bursary_levels'),
    path('api/resources/recommended/', views.get_suitable_resources, name='get_suitable_resources'),
    path('api/resources/posted_by/<str:username>/',views.resources_posted_by, name='resources_posted_by'),
    path('api/resources/commented_by/<str:username>/',views.resources_commented_by, name='resources_commented_by'),
]