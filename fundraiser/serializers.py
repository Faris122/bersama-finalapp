from rest_framework import serializers
from django.db.models import Sum
from django.utils.timezone import now
from .models import *

class FundraiserSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    amount_raised = serializers.SerializerMethodField()

    def get_amount_raised(self, obj):
        # Gets the amount raised based on the different amounts from donations
        total = obj.funds.aggregate(total_amount=Sum('amount'))['total_amount']
        return total if total else 0

    class Meta:
        model = Fundraiser
        fields = '__all__'
        
    
class FundraiserDetailSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    amount_raised = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Fundraiser
        fields = '__all__'
    
    def get_amount_raised(self, obj):
        total = obj.funds.aggregate(total_amount=Sum('amount'))['total_amount']
        return total if total else 0
    
    def get_comments(self, obj):
        comments = obj.comments.filter(parent=None).order_by('-created_at')
        return FundraiserCommentSerializer(comments, many=True).data

class PaymentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Payment
        fields = '__all__'
    
    def validate(self, data):
        # Ensure that donations are not allowed after the fundraiser's end_date
        fundraiser = data.get('fundraiser')  # Get the fundraiser from the request data
        
        if fundraiser.end_date < now():  # Check if the fundraiser has ended
            raise serializers.ValidationError("Donations are no longer accepted for this fundraiser.")

        return data
    
class PaymentExpandedSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    fundraiser = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = '__all__'

    def get_fundraiser(self, obj):
        return FundraiserSerializer(obj.fundraiser).data
    
    def validate(self, data):
        # Ensure that donations are not allowed after the fundraiser's end_date
        fundraiser = data.get('fundraiser')  # Get the fundraiser from the request data
        
        if fundraiser.end_date < now():  # Check if the fundraiser has ended
            raise serializers.ValidationError("Donations are no longer accepted for this fundraiser.")

        return data
    
class FundraiserCommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = FundraiserComment
        fields = ['id', 'content', 'author_username', 'created_at', 'parent', 'replies']

    def get_replies(self, obj):
        if obj.replies.exists():
            return FundraiserCommentSerializer(obj.replies.all(), many=True).data
        return []
    
class FundraiserCommentExpandedSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()

    class Meta:
        model = FundraiserComment
        fields = ['id', 'content','post', 'author_username', 'created_at', 'parent', 'replies']

    def get_post(self, obj):
        return FundraiserSerializer(obj.post).data

    def get_replies(self, obj):
        if obj.replies.exists():
            return FundraiserCommentSerializer(obj.replies.all(), many=True).data
        return []


    