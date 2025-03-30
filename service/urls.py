from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # Service Endpoints
    # Page View
    path('services/', views.service_list, name='service_list'),
    path('services/create/', views.create_service, name='create_service'),
    path('services/map/', views.service_map, name='service_map'),
    path('services/<int:pk>/', views.service_detail, name='service_detail'),

    # API View
    path('api/services/', views.service_list_api, name='service_list_api'),
    path('api/services/create/', views.create_service_api, name='create_service_api'),
    path('api/services/<int:pk>/', views.service_detail_api, name='service_detail_api'),
    path('api/services/<int:pk>/add_comment/', views.add_service_comment_api, name='add_service_comment_api'),
    path('api/services/comments/<int:comment_id>/delete/', views.delete_service_comment_api, name='delete_service_comment_api'),
    path('api/services/categories/', views.service_categories_list_api, name='service_categories_list_api'),
    path('api/services/search/',views.search_services, name='search_services'),
    path('api/services/commented_by/<str:username>/', views.services_commented_by, name='services_commented_by'),

    # Event Endpoints
    # Page View
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/map/', views.event_map, name='event_map'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),

    # API View
    path('api/events/', views.event_list_api, name='event_list_api'),
    path('api/events/create/', views.create_event_api, name='create_event_api'),
    path('api/events/running/', views.event_running_api, name='event_running_api'),
    path('api/events/<int:pk>/', views.event_detail_api, name='event_detail_api'),
    path('api/events/<int:pk>/add_comment/', views.add_event_comment_api, name='add_event_comment_api'),
    path('api/events/comments/<int:comment_id>/delete/', views.delete_event_comment_api, name='delete_event_comment_api'),
    path('api/events/categories/', views.event_categories_list_api, name='event_categories_list_api'),
    path('api/events/search/',views.search_events, name='search_events'),
    path('api/events/commented_by/<str:username>/', views.events_commented_by, name='events_commented_by'),
]
