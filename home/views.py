from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from .models import *
from django.contrib.auth.decorators import login_required

# View for home
def home(request):
    return render(request, 'home.html')



