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
from django.http import Http404, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from django.core.exceptions import PermissionDenied
from django.db.models import Q

def login_user(request):
    return render(request, 'login.html')

def register_user(request):
    return render(request, 'registration.html')

def logout_user(request):
    logout(request)
    return redirect('home')

def profile(request, username=None):
    # If username is none, go to user's profile, if not, flag 404
    if username is None:
        if not request.user.is_authenticated:
            raise Http404("Profile not found.")
        profile = request.user.profile
        is_own = True
        api_url = "/api/profile"
        username = request.user.username
    elif username == request.user.username:
        profile = request.user.profile
        is_own = True
        api_url = "/api/profile"
    else:
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)
        is_own = False
        api_url = "/api/profile/"+username

    return render(request, 'profile.html', {'profile': profile, 'is_own': is_own,'api_url':api_url,'username':username})

@login_required
def edit_profile(request):
    return render(request, 'edit_profile.html')

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user_api(request): 
    # Registers a user
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def login_user_api(request): 
    # Logs in a user
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        return Response({"message": "Login successful", "username": user.username}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout_user_api(request):
    # Logs out a user (not used)
    if request.user.is_authenticated:
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "User is not logged in"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def profile_api(request, username=None):
    # Displays profile using API, same rules as page view above
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
    # Edit profile
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

            # Validate and update financial profile
            financial_serializer = FinancialProfileSerializer(financial_profile, data=financial_data, partial=True,context={'request':request})
            if financial_serializer.is_valid():
                financial_serializer.save()
            else:
                return Response(financial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        updated_data = serializer.data
        if profile.needs_help:
            updated_data['financial_profile'] = FinancialProfileSerializer(profile.financial_profile,context={'request':request}).data

        return Response(updated_data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def search_address(request):
    # Fetch addresses from Nominatim API
    query = request.GET.get('query', '').strip()
    if not query:
        return Response({'error': 'Query parameter is required'}, status=status.HTTP_404_NOT_FOUND)

    # Initialise Nominatim API
    geolocator = Nominatim(user_agent="finalapp/0.1")

    try:
        # Perform the geocoding request
        locations = geolocator.geocode(query, exactly_one=False, timeout=5)
        
        if locations:
            print(locations[0])
            # Format the response data
            data = [{
                'display_name': location.address,
                'lat': location.latitude,
                'lon': location.longitude,
            } for location in locations]
            return Response(data)
        else:
            return Response({'error': 'No results found'}, status=status.HTTP_404_NOT_FOUND)

    except GeocoderTimedOut:
        return Response({'error': 'Geocoding service timed out'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except GeocoderServiceError as e:
        return Response({'error': f'Geocoding service error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@login_required
def chat_list(request):
    # Page view for chat list
    return render(request, 'chat_list.html')

@login_required
def chat_view(request, recipient_username):
    # Displays chat view
    # Get the recipient user
    recipient = get_object_or_404(User, username=recipient_username)

    # Ensure the user is not trying to chat with themselves
    if request.user == recipient:
        raise PermissionDenied("You cannot chat with yourself.")

    # Retrieve or create a chat session
    chat = Chat.objects.filter(
        (models.Q(user1=request.user) & models.Q(user2=recipient)) |
        (models.Q(user1=recipient) & models.Q(user2=request.user))
    ).first()

    if not chat:
        # Check if the recipient's DMs are open (only if initiating, dm closed users can initiate DMs)
        if not recipient.profile.is_dm_open:
            raise PermissionDenied("This user has disabled direct messages.")
        # Create a new chat session
        chat = Chat.objects.create(user1=request.user, user2=recipient)

    # Fetch previous messages (older, not used)
    messages = Message.objects.filter(chat=chat).order_by('timestamp')

    # Pass context to the template
    context = {
        'chat_id': chat.id,
        'chat_partner_username': recipient.username,
        'messages': messages
    }

    return render(request, 'chat.html', context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_list_api(request):
    # Return chats where the current user is a participant
    chats = Chat.objects.filter(
        models.Q(user1=request.user) | models.Q(user2=request.user)
    )
    serializer = ChatSerializer(chats, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def create_or_get_chat_api(request):
    # Create or get a chat based on other username request
    other_username = request.GET.get('other_username')
    if not other_username:
        return Response({'error': 'Other user\'s username is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        other = User.objects.get(username=other_username)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if the other user has DMs open
    if not other.profile.is_dm_open:
        return Response({'error': 'This user has disabled direct messaging'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Ensure the user is not trying to chat with themselves
    if request.user == other:
        return Response({'error': 'You cannot chat with yourself'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Find or create a chat between the two users
    chat = Chat.objects.filter(
        (models.Q(user1=request.user) & models.Q(user2=other)) |
        (models.Q(user1=other) & models.Q(user2=request.user))
    ).first()

    if not chat:
        # Create a new chat
        chat = Chat.objects.create(user1=request.user, user2=other)
        created = True
    else:
        created = False

    # Serialize the chat
    serializer = ChatSerializer(chat, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message_api(request, chat_id):
    # Sends a message through the API (Non functional, intended to demonstrate the use of API, normal messages pass thru websockets)
    try:
        chat = Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        return Response({'error': 'Chat not found'}, status=404)
    
    # Ensure the current user is a participant.
    if request.user not in [chat.user1, chat.user2]:
        return Response({'error': 'Not authorized'}, status=403)
    
    content = request.data.get('content')
    if not content:
        return Response({'error': 'Content is required'}, status=400)
    
    message = Message.objects.create(chat=chat, sender=request.user, content=content)
    serializer = MessageSerializer(message)
    return Response(serializer.data, status=201)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_messages_api(request, chat_id):
    # Gets chat messages from the API (no serialiser used)
    messages = Message.objects.filter(chat_id=chat_id).order_by('timestamp')
    messages_data = [
        {
            'id': message.id,  # Include message ID
            'sender': message.sender.username,
            'message': message.content,
            'timestamp': message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'read': message.read,  # Include read status
        }
        for message in messages
    ]
    return JsonResponse({'messages': messages_data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def total_unread_api(request):
    # Gets the total unread count for display on navbar
    # Get all chats where the user is a participant
    chats = Chat.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    )

    # Calculate the total unread count
    total_unread = 0
    for chat in chats:
        # Count unread messages where the sender is not the current user
        unread_count = Message.objects.filter(
            chat=chat,
            read=False,
        ).exclude(sender=request.user).count()
        total_unread += unread_count

    return Response({'total_unread': total_unread})
