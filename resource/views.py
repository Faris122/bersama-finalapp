from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from .models import *
from account.models import *
from django.contrib.auth.decorators import login_required

def resource_list(request):
    resources = Resource.objects.all()
    return render(request, 'resources.html', {'resources': resources})

def resource_detail(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    comments = resource.comments.all()
    return render(request, 'resource_detail.html', {
        'resource': resource, 'comments': comments
    })

def resource_detail(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    comments = resource.comments.filter(parent=None).order_by('-created_at')  # Top-level comments
    form = ResourceCommentForm()

    if request.method == 'POST':
        form = ResourceCommentForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                parent_id = request.POST.get('parent_id')
                comment = form.save(commit=False)
                comment.post = resource
                comment.author = request.user
                if parent_id:  # If replying to a comment
                    parent_comment = ResourceComment.objects.get(id=parent_id)
                    comment.parent = parent_comment
                comment.save()
            return redirect('resource_detail', pk=pk)

    context = {
        'resource': resource,
        'comments': comments,
        'form': form,
    }
    return render(request, 'resource_detail.html', context)

@login_required
def create_resource(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.author = request.user  # Assign the current logged-in user
            resource.save()
            form.save_m2m()  # Save many-to-many relationships
            return redirect('resource_detail', resource_id=resource.id)
    else:
        form = ResourceForm()
    return render(request, 'create_resource.html', {'form': form})