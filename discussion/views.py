from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.contrib.auth.models import User
from .models import *
from account.models import *
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from .serializers import *

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

@api_view(['GET'])
def discussion_list_api(request):
    """API to get a list of discussions."""
    discussions = Discussion.objects.all()
    serializer = DiscussionSerializer(discussions, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_discussion_api(request):
    """API to create a new discussion."""
    serializer = DiscussionCreateSerializer(data=request.data)
    if serializer.is_valid():
        discussion = serializer.save(author=request.user)  # Attach the logged-in user as the author
        return Response({
            'message': 'Discussion created successfully!',
            'discussion': {
                'id': discussion.id,
                'title': discussion.title,
                'content': discussion.content,
                'categories': [category.name for category in discussion.categories.all()],
                'author_username': discussion.author.username,
                'created_at': discussion.created_at
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def discussion_detail_api(request, pk):
    try:
        discussion = Discussion.objects.get(pk=pk)
    except Discussion.DoesNotExist:
        return Response({'error': 'Discussion not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = DiscussionDetailSerializer(discussion)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment_api(request, pk):
    try:
        discussion = Discussion.objects.get(pk=pk)
    except Discussion.DoesNotExist:
        return Response({'error': 'Discussion not found'}, status=status.HTTP_404_NOT_FOUND)

    parent_id = request.data.get('parent_id')
    serializer = DiscussionCommentSerializer(data=request.data)
    if serializer.is_valid():
        comment = serializer.save(author=request.user, post=discussion)
        if parent_id:
            try:
                parent_comment = DiscussionComment.objects.get(id=parent_id)
                comment.parent = parent_comment
                comment.save()
            except DiscussionComment.DoesNotExist:
                return Response({'error': 'Parent comment not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(DiscussionCommentSerializer(comment).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def discussion_categories_list_api(request):
    """API to fetch all discussion categories."""
    categories = DiscussionCategory.objects.all()
    serializer = DiscussionCategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)