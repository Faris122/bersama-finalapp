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
def discussion_list(request):
    discussions = Discussion.objects.all()
    return render(request, 'discussions.html', {'discussions': discussions})

def discussion_detail(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk)
    comments = discussion.comments.filter(parent=None).order_by('-created_at')  # Top-level comments
    form = DiscussionCommentForm()

    if request.method == 'POST':
        form = DiscussionCommentForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                parent_id = request.POST.get('parent_id')
                comment = form.save(commit=False)
                comment.post = discussion
                comment.author = request.user
                if parent_id:  # If replying to a comment
                    parent_comment = DiscussionComment.objects.get(id=parent_id)
                    comment.parent = parent_comment
                comment.save()
            return redirect('discussion_detail', pk=pk)

    context = {
        'discussion': discussion,
        'comments': comments,
        'form': form,
    }
    return render(request, 'discussion_detail.html', context)

@login_required
def create_discussion(request):
    if request.method == 'POST':
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.author = request.user
            discussion.save()
            form.save_m2m()  # Save categories
            return redirect('discussion_list')
    else:
        form = DiscussionForm()
    return render(request, 'create_discussion.html', {'form': form})