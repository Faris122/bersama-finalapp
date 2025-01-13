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

# View to display the logged-in user's profile
@login_required
def my_profile(request):
    profile = request.user.profile  # Access the profile of the logged-in user
    return render(request, 'profile.html', {'profile': profile, 'is_own':True})

# View to display other users' profiles by username
def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    return render(request, 'profile.html', {'profile': profile,  'is_own':False})

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
@permission_classes([IsAuthenticated])
def my_profile_api(request):
    """API to view the logged-in user's profile."""
    profile = request.user.profile
    serializer = ProfileSerializer(profile)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def view_profile_api(request, username):
    """API to view another user's profile by username."""
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    serializer = ProfileSerializer(profile)
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