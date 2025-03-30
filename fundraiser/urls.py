from django.urls import path
from . import views

urlpatterns = [
    # Fundraiser Endpoints
    # Page Views
    path('fundraisers/', views.fundraiser_list, name='fundraiser_list'),
    path('fundraisers/<int:pk>/', views.fundraiser_detail, name='fundraiser_detail'),
    path('fundraisers/<int:pk>/donation/', views.donation_page, name='donation_page'),
    path('fundraisers/create/', views.create_fundraiser, name='create_fundraiser'),
    # API Views
    path('api/fundraisers/', views.fundraiser_list_api, name='fundraiser_list_api'),
    path('api/fundraisers/<int:pk>/', views.fundraiser_detail_api, name='fundraiser_detail_api'),
    path('api/fundraisers/create/', views.create_fundraiser_api, name='create_fundraiser_api'),
    path('api/fundraisers/search/', views.search_fundraiser_api, name='search_fundraiser_api'),
    path('api/fundraisers/active/', views.active_fundraiser_api, name='active_fundraiser_api'),
    path('api/fundraisers/posted_by/<str:username>/',views.fundraisers_posted_by, name='fundraiser_posted_by'),
    path('api/fundraisers/commented_by/<str:username>/',views.fundraisers_commented_by, name='fundraiser_commented_by'),
    path('api/fundraisers/donated_by/<str:username>/',views.fundraisers_donated_by, name='fundraisers_donated_by'),

    # Comment API Views
    path('api/fundraisers/<int:pk>/add_comment/', views.add_comment_api, name='add_comment_api'),
    path('api/fundraisers/comments/<int:comment_id>/delete/', views.delete_comment_api, name='delete_comment_api'),
    # Donation API Views
    path('api/fundraisers/<int:pk>/donations/', views.fundraiser_donations_api, name='fundraiser_donations_api'),
    path('api/donations/create/', views.create_donation_api, name='create-donation'),
    path('api/donations/user/<str:username>/', views.user_donations_api, name='user-donations'),
    
]