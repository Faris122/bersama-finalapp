from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied, BadRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *

def fundraiser_list(request):
    return render(request,'fundraiser_list.html')

def fundraiser_detail(request,pk):
    fundraiser = get_object_or_404(Fundraiser,pk=pk)
    return render(request,'fundraiser.html', {'fundraiser':fundraiser})

def donation_page(request, pk):
    fundraiser = get_object_or_404(Fundraiser, pk=pk)
    if timezone.now() > fundraiser.end_date:
        raise BadRequest("Donations are no longer accepted for this fundraiser.")
    return render(request, 'donation.html', {'fundraiser': fundraiser})

def create_fundraiser(request):
        user = request.user

        # Ensure the user has a profile
        if not hasattr(user, 'profile'):
            raise PermissionDenied("User does not have a profile.")

        # Check if the user is allowed to create a fundraiser
        if user.profile.role == 'Public' and user.profile.needs_help:
            if Fundraiser.objects.filter(user=user, end_date__gt=timezone.now()).exists():
                raise PermissionDenied("You can only create one fundraiser as a user who needs help.")
        elif user.profile.role == 'Public' and not user.profile.needs_help:
            raise PermissionDenied("You are not allowed to create a fundraiser as a user who does not need help.")
        return render(request, 'new_fundraiser.html')

@api_view(['GET'])
def fundraiser_list_api(request):
    fundraisers = Fundraiser.objects.all()
    serializer = FundraiserSerializer(fundraisers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def fundraiser_detail_api(request, pk):
    fundraiser = get_object_or_404(Fundraiser, pk=pk)
    serializer = FundraiserDetailSerializer(fundraiser)
    return Response(serializer.data)

@api_view(['GET'])
def fundraiser_donations_api(request, pk):
    fundraiser = get_object_or_404(Fundraiser, pk=pk)
    donations = Payment.objects.filter(fundraiser=fundraiser).order_by('-created_at')
    serializer = PaymentSerializer(donations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def user_donations_api(request, username):
    donations = Payment.objects.filter(user__username=username)
    serializer = PaymentSerializer(donations, many=True)
    return Response(serializer.data)

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_fundraiser_api(request):
    if not request.user.is_authenticated:
        return Response({"detail": "User not logged in."}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'POST':
        serializer = FundraiserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Save the fundraiser and handle ValidationError
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                # Return a 400 Bad Request response with the error message
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_donation_api(request):
    if request.method == 'POST':
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            # If the user is authenticated, associate the donation with the user
            if request.user.is_authenticated:
                serializer.save(user=request.user)
            else:
                serializer.save(user=None)  # Anonymous donation
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def search_fundraiser_api(request):
    query = request.GET.get('q', '')  # Search query

    fundraisers = Fundraiser.objects.all()

    # Filter by search query (title/content)
    if query:
        fundraisers = fundraisers.filter(title__icontains=query) | fundraisers.filter(description__icontains=query)

    # Serialize and return results
    serializer = FundraiserSerializer(fundraisers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment_api(request, pk):
    try:
        fundraiser = Fundraiser.objects.get(pk=pk)
    except Fundraiser.DoesNotExist:
        return Response({'error': 'Fundraiser not found'}, status=status.HTTP_404_NOT_FOUND)

    parent_id = request.data.get('parent_id')
    serializer = FundraiserCommentSerializer(data=request.data)
    if serializer.is_valid():
        comment = serializer.save(author=request.user, post=fundraiser)
        if parent_id:
            try:
                parent_comment = FundraiserComment.objects.get(id=parent_id)
                comment.parent = parent_comment
                comment.save()
            except FundraiserComment.DoesNotExist:
                return Response({'error': 'Parent comment not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(FundraiserCommentSerializer(comment).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment_api(request, comment_id):
    try:
        comment = FundraiserComment.objects.get(id=comment_id)
    except FundraiserComment.DoesNotExist:
        return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

    # Ensure that the logged-in user is the author of the comment
    if comment.author != request.user:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def active_fundraiser_api(request):
    # Gets all fundraisers that is in progress and amount raised < goal amount
    # Get current datetime
    now = timezone.now()
    
    # Filter fundraisers that are in progress and amount_raised < goal_amount
    fundraisers = Fundraiser.objects.annotate(
        total_donations=Sum('funds__amount')
    ).filter(
        start_date__lte=now,
        end_date__gte=now
    ).exclude(
        total_donations__gte=models.F('goal_amount')
    )
    
    serializer = FundraiserSerializer(fundraisers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def fundraisers_posted_by(request, username):
    # API to get a list of fundraisers by a single user
    user = get_object_or_404(User, username=username)
    fundraisers = Fundraiser.objects.filter(user=user).order_by('-created_at')
    serializer = FundraiserSerializer(fundraisers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def fundraisers_commented_by(request, username):
    # API to get a list of comments by a single user
    user = get_object_or_404(User, username=username)
    comments = FundraiserComment.objects.filter(author=user).order_by('-created_at')
    serializer = FundraiserCommentExpandedSerializer(comments, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def fundraisers_donated_by(request, username):
    # API to get a list of donations by a single user
    user = get_object_or_404(User, username=username)
    donations = Payment.objects.filter(user=user).order_by('-created_at')
    serializer = PaymentExpandedSerializer(donations, many=True)
    return Response(serializer.data)