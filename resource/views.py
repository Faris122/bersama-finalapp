from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
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
from django.http import JsonResponse

def resource_list(request):
    # Get the 'categories' query parameter from the URL
    categories = request.GET.getlist('categories',[])
    levels = request.GET.getlist('levels',[]) #For Bursaries
    
    # Pass the categories to the template context
    context = {
        'initial_categories': categories,
        'initial_levels': levels
    }
    return render(request, 'resource_list.html',context)
def bursary_list(request):
    # Get the 'categories' query parameter from the URL
    query = request.GET.get('q')
    levels = request.GET.getlist('levels') #For Bursaries
    
    # Pass the categories to the template context
    context = {
        'initial_query': query,
        'initial_levels': levels
    }
    return render(request, 'bursary_list.html',context)


def resource_detail(request, pk):
    resource = get_object_or_404(Resource, pk=pk)

    context = {
        'resource': resource
    }
    return render(request, 'resource.html', context)

@login_required
def create_resource(request):

    return render(request, 'new_resource.html')

@api_view(['GET'])
def resource_list_api(request):
    # API to get a list of resources (excluding bursaries) 
    
    resources = Resource.objects.filter(bursary__isnull=True)
    
    serializer = ResourceSerializer(resources, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def bursary_list_api(request):
    # API to get a list of resources (excluding bursaries)
    
    resources = Bursary.objects.all()
    
    serializer = BursarySerializer(resources, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_resource_api(request):
    # API to create a new resource
    serializer = ResourceCreateSerializer(data=request.data)
    if serializer.is_valid():
        resource = serializer.save(author=request.user)  # Attach the logged-in user as the author
        return Response({
            'message': 'Resource created successfully!',
            'resource': {
                'id': resource.id,
                'title': resource.title,
                'content': resource.content,
                'categories': [category.name for category in resource.categories.all()],
                'author_username': resource.author.username,
                'created_at': resource.created_at
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_bursary_api(request):
    # API to create a new bursary (child of resource)
    serializer = BursaryCreateSerializer(data=request.data)
    if serializer.is_valid():
        resource = serializer.save(author=request.user)
        return Response({
            'message': 'Resource created successfully!',
            'resource': {
                'id': resource.id,
                'title': resource.title,
                'content': resource.content,
                'author_username': resource.author.username,
                'created_at': resource.created_at
            }
        }, status=status.HTTP_201_CREATED)
    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def resource_detail_api(request, pk):
    # Shows the detail of either bursary or generic resource
    # Conditional to check if bursary or resource
    try:
        resource = Bursary.objects.get(pk=pk)
        serializer_class = BursaryDetailSerializer
        is_bursary = True
    except Bursary.DoesNotExist:
        try:
            resource = Resource.objects.get(pk=pk)
            serializer_class = ResourceDetailSerializer
            is_bursary = False
        except Resource.DoesNotExist:
            return Response({'error': 'Resource not found'}, status=status.HTTP_404_NOT_FOUND)

    # Use the appropriate serializer
    serializer = serializer_class(resource, context={'request': request})
    response_data = serializer.data
    response_data["is_bursary"] = is_bursary
    
    return Response(response_data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment_api(request, pk):
    # API to add comment based on parent_id and resource
    resource = get_object_or_404(Resource,pk=pk)

    parent_id = request.data.get('parent_id')
    serializer = ResourceCommentSerializer(data=request.data)
    if serializer.is_valid():
        comment = serializer.save(author=request.user, post=resource)
        if parent_id:
            try:
                parent_comment = ResourceComment.objects.get(id=parent_id)
                comment.parent = parent_comment
                comment.save()
            except ResourceComment.DoesNotExist:
                return Response({'error': 'Parent comment not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ResourceCommentSerializer(comment).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment_api(request, comment_id):
    # Deletes comment based on comment ID
    comment = get_object_or_404(ResourceComment,id=comment_id)

    # Ensure that the logged-in user is the author of the comment
    if comment.author != request.user:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def resource_categories_list_api(request):
    # API to fetch all resource categories
    categories = ResourceCategory.objects.all()
    serializer = ResourceCategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def search_resources(request):
    # Search resources by title, content, or filter by multiple categories
    query = request.GET.get('q', '')  # Search query
    categories = request.GET.get('categories', '')  # Comma-separated category names

    resources = Resource.objects.filter(bursary__isnull=True)
    

    # Filter by search query (title/content)
    if query:
        resources = resources.filter(title__icontains=query) | resources.filter(content__icontains=query)

    # Filter by multiple categories
    if categories:
        category_list = categories.split(',')
        resources = resources.filter(categories__name__in=category_list) \
                                 .annotate(category_count=Count('categories')) \
                                 .filter(category_count=len(category_list))

    # Serialize and return results
    serializer = ResourceSerializer(resources, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def search_bursaries(request):
    # Search bursaries by query or filter by level
    query = request.GET.get('q', '')  # Search query
    levels = request.GET.get('levels', '')  # Comma-separated levels names

    bursaries = Bursary.objects.all()

    # Filter by search query
    if query:
        bursaries = bursaries.filter(title__icontains=query) | bursaries.filter(content__icontains=query)

    # Filter by level
    if levels:
        level_list = levels.split(',')
        bursaries = bursaries.filter(level__in=level_list)

    serializer = BursarySerializer(bursaries, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_resource_api(request, pk):
    # API to delete resource
    try:
        resource = Resource.objects.get(pk=pk)
    except Resource.DoesNotExist:
        return Response({"error": "Resource not found"}, status=status.HTTP_404_NOT_FOUND)

    # Ensure only author can delete the resource
    if resource.author != request.user:
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    resource.delete()
    return Response({"message": "Resource deleted successfully"}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_bursary_levels(request):
    # Fetch available bursary levels
    levels = [level[0] for level in Bursary.LEVEL_CHOICES]  # Extract level values from choices
    return JsonResponse(levels, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_suitable_resources(request):
    # Returns a list of resources suited to the user's financial profile
    user = request.user

    # Ensure the user has a financial profile
    if not hasattr(user, 'profile') or not hasattr(user.profile, 'financial_profile'):
        return Response({"error": "Financial profile not found"}, status=400)

    financial_profile = user.profile.financial_profile

    # Extract financial details
    user_income = financial_profile.own_income
    household_income = financial_profile.household_income
    household_members = financial_profile.household_members
    has_children = financial_profile.has_children
    has_elderly = financial_profile.has_elderly

    # This is to be customisable based on what is found in Financial Profile and the categories, in populate.py

    # Build query for filtering resources
    resource_query = Q()

    # Income-based filtering
    resource_query &= (
        Q(min_income_pc__lte=household_income/household_members) | Q(min_income_pc__isnull=True)
    ) & (
        Q(max_income_pc__gte=household_income/household_members) | Q(max_income_pc__isnull=True)
    ) & (
        Q(min_income_gross__lte=household_income) | Q(min_income_gross__isnull=True)
    ) & (
        Q(max_income_gross__gte=household_income) | Q(max_income_gross__isnull=True)
    )

    # Consider categorical preferences based on situation
    category_filters = Q()
    if has_children:
        category_filters |= Q(categories__name="Families") | Q(categories__name="Students")
    if has_elderly:
        category_filters |= Q(categories__name="Families")
    if household_income < 2000: # Low Income Threshold, Singapore is about 1900-2200
        category_filters |= Q(categories__name="Voucher") | Q(categories__name="Subsidy")
    
    # Apply category filters based on preferences
    if category_filters:
        resource_query &= category_filters

    # Fetch resources based on query
    resources = Resource.objects.filter(resource_query).distinct()

    # Serialize and return results
    serializer = ResourceSerializer(resources, many=True)
    return Response(serializer.data, status=200)

@api_view(['GET'])
def resources_posted_by(request, username):
    # API to get a list of fundraisers by a single user
    user = get_object_or_404(User, username=username)
    fundraisers = Resource.objects.filter(author=user).order_by('-created_at')
    serializer = ResourceSerializer(fundraisers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def resources_commented_by(request, username):
    # API to get a list of comments by a single user
    user = get_object_or_404(User, username=username)
    comments = ResourceComment.objects.filter(author=user).order_by('-created_at')
    serializer = ResourceCommentExpandedSerializer(comments, many=True)
    return Response(serializer.data)