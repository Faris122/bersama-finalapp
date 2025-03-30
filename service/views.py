from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from .models import *
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.utils import timezone

def service_list(request):
    categories = request.GET.getlist('categories',[])

    context = {'initial_categories':categories}
    return render(request, 'service_list.html', context)

def create_service(request):

    return render(request, 'new_service.html', {})

def service_map(request):
    query = request.GET.get('q')
    categories = request.GET.get('categories')
    return render(request, 'services_map.html', {'query':query,'categories':categories})

def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    context = {
        'service': service,
    }
    return render(request, 'service.html', context)

@api_view(['GET'])
def service_list_api(request):
    # Check for latitude and longitude in query parameters first
    user_lat = request.GET.get('latitude')
    user_lon = request.GET.get('longitude')
    
    if user_lat is not None and user_lon is not None:
        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
        except ValueError:
            user_lat, user_lon = None, None
    elif request.user.is_authenticated:
        # Fallback to the profile location if no query parameters
        if (request.user.profile.latitude and request.user.profile.longitude):
            user_lat = request.user.profile.latitude
            user_lon = request.user.profile.longitude
        else:
            user_lat, user_lon = None, None

    services = Service.objects.all()
    serializer = ServiceSerializer(
        services, 
        many=True, 
        context={'user_lat': user_lat, 'user_lon': user_lon}
    )
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_service_api(request):
    # API to create a new service
    serializer = ServiceCreateSerializer(data=request.data)
    if serializer.is_valid():
        service = serializer.save()  # Attach the logged-in user as the author
        return Response({
            'message': 'Service created successfully!',
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def service_detail_api(request, pk):
    try:
        service = Service.objects.get(pk=pk)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ServiceDetailSerializer(service)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_service_comment_api(request, pk):
    try:
        service = Service.objects.get(pk=pk)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)

    parent_id = request.data.get('parent_id')
    serializer = ServiceCommentSerializer(data=request.data)
    if serializer.is_valid():
        comment = serializer.save(author=request.user, service=service)
        if parent_id:
            try:
                parent_comment = ServiceComment.objects.get(id=parent_id)
                comment.parent = parent_comment
                comment.save()
            except ServiceComment.DoesNotExist:
                return Response({'error': 'Parent comment not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ServiceCommentSerializer(comment).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_service_comment_api(request, comment_id):
    try:
        comment = ServiceComment.objects.get(id=comment_id)
    except ServiceComment.DoesNotExist:
        return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

    # Ensure that the logged-in user is the author of the comment
    if comment.author != request.user:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def service_categories_list_api(request):
    # API to fetch all service categories
    categories = ServiceCategory.objects.all()
    serializer = ServiceCategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def search_services(request):
    # Search services by title, content, or filter by multiple categories
    query = request.GET.get('q', '')  # Search query
    categories = request.GET.get('categories', '')  # Comma-separated category names
    user_lat = request.GET.get('latitude')
    user_lon = request.GET.get('longitude')
    
    if user_lat is not None and user_lon is not None:
        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
        except ValueError:
            user_lat, user_lon = None, None
    elif request.user.is_authenticated:
        # Fallback to the profile location if no query parameters
        if (request.user.profile.latitude and request.user.profile.longitude):
            user_lat = request.user.profile.latitude
            user_lon = request.user.profile.longitude
        else:
            user_lat, user_lon = None, None
    
    services = Service.objects.all()

    # Filter by search query (title/content)
    if query:
        services = services.filter(title__icontains=query) | services.filter(content__icontains=query)

    # Filter by multiple categories
    if categories:
        category_list = categories.split(',')
        services = services.filter(categories__name__in=category_list) \
                                 .annotate(category_count=Count('categories')) \
                                 .filter(category_count=len(category_list))

    # Serialize and return results
    serializer = ServiceSerializer(services, many=True, 
        context={'user_lat': user_lat, 'user_lon': user_lon})
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def services_commented_by(request, username):
    # API to get a list of comments by a single user
    user = get_object_or_404(User, username=username)
    comments = ServiceComment.objects.filter(author=user).order_by('-created_at')
    serializer = ServiceCommentExpandedSerializer(comments, many=True)
    return Response(serializer.data)

def event_list(request):
    categories = request.GET.getlist('categories',[])

    context = {'initial_categories':categories}
    return render(request, 'event_list.html', context)

def create_event(request):

    return render(request, 'new_event.html', {})

def event_map(request):
    query = request.GET.get('q')
    categories = request.GET.get('categories')
    return render(request, 'events_map.html', {'query':query,'categories':categories})

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    context = {
        'event': event,
    }
    return render(request, 'event.html', context)

@api_view(['GET'])
def event_list_api(request):
    # Check for latitude and longitude in query parameters first
    user_lat = request.GET.get('latitude')
    user_lon = request.GET.get('longitude')
    
    if user_lat is not None and user_lon is not None:
        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
        except ValueError:
            user_lat, user_lon = None, None
    elif request.user.is_authenticated:
        # Fallback to the profile location if no query parameters
        if (request.user.profile.latitude and request.user.profile.longitude):
            user_lat = request.user.profile.latitude
            user_lon = request.user.profile.longitude
        else:
            user_lat, user_lon = None, None

    events = Event.objects.all()
    serializer = EventSerializer(
        events, 
        many=True, 
        context={'user_lat': user_lat, 'user_lon': user_lon}
    )
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_event_api(request):
    # API to create a new event
    serializer = EventCreateSerializer(data=request.data)
    if serializer.is_valid():
        event = serializer.save()
        return Response({
            'message': 'Event created successfully!',
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def event_detail_api(request, pk):
    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = EventDetailSerializer(event)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_event_comment_api(request, pk):
    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

    parent_id = request.data.get('parent_id')
    serializer = EventCommentSerializer(data=request.data)
    if serializer.is_valid():
        comment = serializer.save(author=request.user, event=event)
        if parent_id:
            try:
                parent_comment = EventComment.objects.get(id=parent_id)
                comment.parent = parent_comment
                comment.save()
            except EventComment.DoesNotExist:
                return Response({'error': 'Parent comment not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(EventCommentSerializer(comment).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_event_comment_api(request, comment_id):
    try:
        comment = EventComment.objects.get(id=comment_id)
    except EventComment.DoesNotExist:
        return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

    # Ensure that the logged-in user is the author of the comment
    if comment.author != request.user:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def event_categories_list_api(request):
    # API to fetch all event categories
    categories = EventCategory.objects.all()
    serializer = EventCategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def search_events(request):
    # Search events by title, content, or filter by multiple categories
    query = request.GET.get('q', '')  # Search query
    categories = request.GET.get('categories', '')  # Comma-separated category names
    running = request.GET.get('running', '') # Events currently in progress or upcoming
    user_lat = request.GET.get('latitude')
    user_lon = request.GET.get('longitude')
    
    if user_lat is not None and user_lon is not None:
        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
        except ValueError:
            user_lat, user_lon = None, None
    elif request.user.is_authenticated:
        # Fallback to the profile location if no query parameters
        if (request.user.profile.latitude and request.user.profile.longitude):
            user_lat = request.user.profile.latitude
            user_lon = request.user.profile.longitude
        else:
            user_lat, user_lon = None, None
    
    events = Event.objects.all()

    # Filter by search query (title/content)
    if query:
        events = events.filter(title__icontains=query) | events.filter(content__icontains=query)

    # Filter by multiple categories
    if categories:
        category_list = categories.split(',')
        events = events.filter(categories__name__in=category_list) \
                                 .annotate(category_count=Count('categories')) \
                                 .filter(category_count=len(category_list))
        
    if running == "true":
        now = timezone.now()
        # Filter events that are upcoming or in progress
        events = Event.objects.filter(
            datetime_end__gte=now  # Events that have not ended
        )
    # Serialize and return results
    serializer = EventSerializer(events, many=True, 
        context={'user_lat': user_lat, 'user_lon': user_lon})
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def event_running_api(request):
    # Show events that are currently in progress
    now = timezone.now()
    
    # Filter events that are upcoming or in progress
    events = Event.objects.filter(
        datetime_end__gte=now  # Events that have not ended
    )
    
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def events_commented_by(request, username):
    # API to get a list of comments by a single user
    user = get_object_or_404(User, username=username)
    comments = EventComment.objects.filter(author=user).order_by('-created_at')
    serializer = EventCommentExpandedSerializer(comments, many=True)
    return Response(serializer.data)
