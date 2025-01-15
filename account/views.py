from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from .models import *
from account.models import *
from django.contrib.auth.decorators import login_required
from django.http import Http404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import *

# Create your views here.
def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html')


def register_user(request):
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # The save method also creates a Profile
            login(request, user)
            return redirect('home')
    else:
        form = ExtendedUserCreationForm()
    return render(request, 'registration.html')

def logout_user(request):
    logout(request)
    return redirect('home')

def profile(request, username=None):
    if username is None:
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            raise Http404("Profile not found.")
        profile = request.user.profile
        is_own = True
        api_url = "/api/profile"
    elif username == request.user.username:
        # If username matches the logged-in user
        profile = request.user.profile
        is_own = True
        api_url = "/api/profile"
    else:
        # Viewing another user's profile
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)
        is_own = False
        api_url = "/api/profile/"+username

    return render(request, 'profile.html', {'profile': profile, 'is_own': is_own,'api_url':api_url})


# View to edit the logged-in user's profile
@login_required
def edit_profile(request):
    profile = request.user.profile  # Access the logged-in user's profile
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('my_profile')  # Redirect back to "my_profile"
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user_api(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def login_user_api(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        return Response({"message": "Login successful", "username": user.username}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout_user_api(request):
    if request.user.is_authenticated:
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "User is not logged in"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def profile_api(request, username=None):
    """
    API to view a user's profile.
    - If `username` is not provided, return the logged-in user's profile.
    - If `username` is provided:
        - Return the specified user's profile.
        - If the username matches the logged-in user, it's treated as their profile.
    """
    if username is None:
        # Check if the user is authenticated
        if request.user.is_authenticated:
            profile = request.user.profile
        else:
            return Response({"error": "No username in query"}, status=status.HTTP_400_BAD_REQUEST)
    elif username == request.user.username:
        # If username matches the logged-in user
        profile = request.user.profile
    else:
        # Viewing another user's profile
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)

    serializer = ProfileSerializer(profile, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_profile_api(request):
    """API to edit the logged-in user's profile."""
    profile = request.user.profile
    serializer = ProfileEditSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)