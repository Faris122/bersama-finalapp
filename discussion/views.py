from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
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

def discussion_list(request):
    # List Page for discussion, makes use of query and categories for search
    query = request.GET.get('q',' ')
    categories = request.GET.getlist('categories')
    
    # Pass the queries and categories to the context
    context = {
        'initial_query' : query,
        'initial_categories': categories,
    }
    return render(request, 'discussion_list.html', context)

def discussion_detail(request, pk):
    # Detail Page for individual discussions
    discussion = get_object_or_404(Discussion, pk=pk)

    context = {
        'discussion': discussion,
    }
    return render(request, 'discussion_detail.html', context)

@login_required
def create_discussion(request):
    # Creating a new discussion
    return render(request, 'new_discussion.html')

@api_view(['GET'])
def discussion_list_api(request):
    # API to get a list of discussions
    discussions = Discussion.objects.all().order_by('-created_at')
    serializer = DiscussionSerializer(discussions, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_discussion_api(request):
    # API to create a new discussion
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
                'created_at': discussion.created_at,
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def discussion_detail_api(request, pk):
    # API to get the details of a discussion
    try:
        discussion = Discussion.objects.get(pk=pk)
    except Discussion.DoesNotExist:
        return Response({'error': 'Discussion not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = DiscussionDetailSerializer(discussion)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment_api(request, pk):
    # API to post comments
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

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment_api(request, comment_id):
    # API to delete comments based on the ID
    try:
        comment = DiscussionComment.objects.get(id=comment_id)
    except DiscussionComment.DoesNotExist:
        return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

    # Ensure that the logged-in user is the author of the comment
    if comment.author != request.user:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def discussion_categories_list_api(request):
    # API to fetch all discussion categories
    categories = DiscussionCategory.objects.all()
    serializer = DiscussionCategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def search_discussions(request):
    # Search discussions by title, content, or filter by multiple categories
    query = request.GET.get('q', '')  # Search query
    categories = request.GET.get('categories', '')  # Comma-separated category names

    discussions = Discussion.objects.all().order_by('-created_at')

    # Filter by search query
    if query:
        discussions = discussions.filter(title__icontains=query) | discussions.filter(content__icontains=query)

    # Filter by multiple categories
    if categories:
        category_list = categories.split(',')
        discussions = discussions.filter(categories__name__in=category_list) \
                                 .annotate(category_count=Count('categories')) \
                                 .filter(category_count=len(category_list))

    serializer = DiscussionSerializer(discussions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def discussions_posted_by(request, username):
    # API to get a list of discussions by a single user
    user = get_object_or_404(User, username=username)
    discussions = Discussion.objects.filter(author=user).order_by('-created_at')
    serializer = DiscussionSerializer(discussions, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def discussions_commented_by(request, username):
    # API to get a list of comments by a single user
    user = get_object_or_404(User, username=username)
    comments = DiscussionComment.objects.filter(author=user).order_by('-created_at')
    serializer = DiscussionCommentExpandedSerializer(comments, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_discussion_api(request, pk):
    # API to delete discussion
    try:
        discussion = Discussion.objects.get(pk=pk)
    except Discussion.DoesNotExist:
        return Response({"error": "Discussion not found"}, status=status.HTTP_404_NOT_FOUND)

    # Ensure only the author can delete the discussion
    if discussion.author != request.user:
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
    discussion.delete()
    return Response({"message": "Discussion deleted successfully"}, status=status.HTTP_200_OK)

