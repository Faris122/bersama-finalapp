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

def login_user(request):
    return render(request, 'login.html')


def register_user(request):
    return render(request, 'registration.html')

def logout_user(request):
    logout(request)
    return redirect('home')

def profile(request, username=None):
    if username is None:
        if not request.user.is_authenticated:
            raise Http404("Profile not found.")
        profile = request.user.profile
        is_own = True
        api_url = "/api/profile"
    elif username == request.user.username:
        profile = request.user.profile
        is_own = True
        api_url = "/api/profile"
    else:
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)
        is_own = False
        api_url = "/api/profile/"+username

    return render(request, 'profile.html', {'profile': profile, 'is_own': is_own,'api_url':api_url})


@login_required
def edit_profile(request):
    return render(request, 'edit_profile.html')

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
    if username is None:
        if request.user.is_authenticated:
            profile = request.user.profile
        else:
            return Response({"error": "No username in query"}, status=status.HTTP_404_NOT_FOUND)
    elif username == request.user.username:
        profile = request.user.profile
    else:
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)

    # Ensure FinancialProfile exists if the user needs help
    financial_profile_data = None

    if profile.needs_help:
        financial_profile, created = FinancialProfile.objects.get_or_create(profile=profile)
        financial_profile_data = FinancialProfileSerializer(financial_profile, context={'request': request}).data

    profile_data = ProfileSerializer(profile, context={'request': request}).data
    profile_data['financial_profile'] = financial_profile_data

    return Response(profile_data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_profile_api(request):
    profile = request.user.profile

    # Check if the user is trying to update 'needs_help' and if they have permission to do so
    if 'needs_help' in request.data and request.data['needs_help'] and profile.role != 'Public':
        return Response({"error": "Only Public users can request help."}, status=status.HTTP_400_BAD_REQUEST)

    # Use ProfileEditSerializer to update profile data
    serializer = ProfileEditSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()

        # If needs_help is set to True, ensure FinancialProfile exists
        if profile.needs_help:
            financial_profile, created = FinancialProfile.objects.get_or_create(profile=profile)

            # Extract financial data from request
            financial_data = {
                'own_income': request.data.get('own_income', financial_profile.own_income),
                'household_income': request.data.get('household_income', financial_profile.household_income),
                'household_members': request.data.get('household_members', financial_profile.household_members),
                'employment_status': request.data.get('employment_status', financial_profile.employment_status),
                'housing_status': request.data.get('housing_status', financial_profile.housing_status),
                'has_elderly': request.data.get('has_elderly', financial_profile.has_elderly),
                'has_children': request.data.get('has_children', financial_profile.has_children)
            }

            # Validate & update financial profile
            financial_serializer = FinancialProfileSerializer(financial_profile, data=financial_data, partial=True,context={'request':request})
            if financial_serializer.is_valid():
                financial_serializer.save()
            else:
                return Response(financial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Prepare updated response data
        updated_data = serializer.data
        if profile.needs_help:
            updated_data['financial_profile'] = FinancialProfileSerializer(profile.financial_profile,context={'request':request}).data

        return Response(updated_data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)