from rest_framework import serializers
from .models import *

class ServiceSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['id', 'title', 'content', 'categories', 'created_at', 'distance','latitude','longitude']

    def get_distance(self, obj): # Gets distance based on context
        user_lat = self.context.get('user_lat')
        user_lon = self.context.get('user_lon')
        if user_lat is not None and user_lon is not None:
            return obj.calculate_distance(user_lat, user_lon)
        return None
    def get_categories(self, obj):
        return [{'id': cat.id, 'name': cat.name} for cat in obj.categories.all()]

class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name']

class ServiceCommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = ServiceComment
        fields = ['id', 'content', 'author_username', 'created_at', 'parent', 'replies']

    def get_replies(self, obj):
        if obj.replies.exists():
            return ServiceCommentSerializer(obj.replies.all(), many=True).data
        return []
    
class ServiceCommentExpandedSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()

    class Meta:
        model = ServiceComment
        fields = ['id', 'content', 'author_username', 'created_at', 'parent', 'replies','post']

    def get_post(self, obj):
        return ServiceSerializer(obj.post).data

    def get_replies(self, obj):
        if obj.replies.exists():
            return ServiceCommentSerializer(obj.replies.all(), many=True).data
        return []
    
class ServiceDetailSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['id', 'title', 'content', 'categories', 'created_at', 'distance','address','latitude','longitude','phone_contact','email_contact','comments']

    def get_distance(self, obj): # Gets distance based on context
        user_lat = self.context.get('user_lat')
        user_lon = self.context.get('user_lon')
        if user_lat is not None and user_lon is not None:
            return obj.calculate_distance(user_lat, user_lon)
        return None
    def get_categories(self, obj):
        return [{'id': cat.id, 'name': cat.name} for cat in obj.categories.all()]
    def get_comments(self, obj):
        comments = obj.comments.filter(parent=None).order_by('-created_at')
        return ServiceCommentSerializer(comments, many=True).data
    
class ServiceCreateSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.all(), 
        required=True, 
        many=True
    )
    latitude = serializers.DecimalField(max_digits=10, decimal_places=5, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=5, required=False, allow_null=True)
    class Meta:
        model = Service
        fields = ['title', 'content', 'categories', 'created_at','address','latitude','longitude','phone_contact','email_contact']
    
class EventSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'content', 'categories', 'created_at', 'distance','latitude','longitude','datetime_start','datetime_end']

    def get_distance(self, obj):
        user_lat = self.context.get('user_lat')
        user_lon = self.context.get('user_lon')
        if user_lat is not None and user_lon is not None:
            return obj.calculate_distance(user_lat, user_lon) # Gets distance based on context
        return None
    def get_categories(self, obj):
        return [{'id': cat.id, 'name': cat.name} for cat in obj.categories.all()]

class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ['id', 'name']

class EventCommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = EventComment
        fields = ['id', 'content', 'author_username', 'created_at', 'parent', 'replies']

    def get_replies(self, obj):
        if obj.replies.exists():
            return EventCommentSerializer(obj.replies.all(), many=True).data
        return []
    
class EventCommentExpandedSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()

    class Meta:
        model = EventComment
        fields = ['id', 'content', 'author_username', 'created_at', 'parent', 'replies','post']

    def get_post(self, obj):
        return EventSerializer(obj.event).data

    def get_replies(self, obj):
        if obj.replies.exists():
            return EventCommentSerializer(obj.replies.all(), many=True).data
        return []
    
class EventDetailSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'content', 'categories', 'created_at', 'distance','address','latitude','longitude','phone_contact','email_contact','comments','datetime_start','datetime_end']

    def get_distance(self, obj):
        user_lat = self.context.get('user_lat')
        user_lon = self.context.get('user_lon')
        if user_lat is not None and user_lon is not None:
            return obj.calculate_distance(user_lat, user_lon) # Gets distance based on context
        return None
    def get_categories(self, obj):
        return [{'id': cat.id, 'name': cat.name} for cat in obj.categories.all()]
    def get_comments(self, obj):
        comments = obj.comments.filter(parent=None).order_by('-created_at')
        return EventCommentSerializer(comments, many=True).data
    
class EventCreateSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        queryset=EventCategory.objects.all(), 
        required=True, 
        many=True
    )
    latitude = serializers.DecimalField(max_digits=10, decimal_places=5, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=5, required=False, allow_null=True)
    class Meta:
        model = Event
        fields = ['title', 'content', 'categories', 'created_at','address','latitude','longitude','phone_contact','email_contact','datetime_start','datetime_end']
    def validate(self, data): #Ensure datetime_start is before datetime_end
        datetime_start = data.get('datetime_start')
        datetime_end = data.get('datetime_end')

        if datetime_start and datetime_end and datetime_start >= datetime_end:
            raise serializers.ValidationError({"datetime_end": "End time must be after the start time."})

        return data

    
    
    