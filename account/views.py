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
    return render(request, 'login.html', {'form': form})

def register_user(request):
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # The save method also creates a Profile
            login(request, user)
            return redirect('home')
    else:
        form = ExtendedUserCreationForm()
    return render(request, 'registration.html', {'form': form})

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