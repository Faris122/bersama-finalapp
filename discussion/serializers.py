from rest_framework import serializers
from .models import *

class DiscussionSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Discussion
        fields = ['id', 'title', 'content', 'author_username', 'categories', 'created_at']

    def get_categories(self, obj):
        return [{'id': cat.id, 'name': cat.name} for cat in obj.categories.all()]

class DiscussionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionCategory
        fields = ['id', 'name']

class DiscussionCreateSerializer(serializers.ModelSerializer):
    # Expect a list of integer IDs for categories
    categories = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = Discussion
        fields = ['title', 'content', 'categories']

    def create(self, validated_data):
        category_ids = validated_data.pop('categories', [])
        discussion = Discussion.objects.create(**validated_data)
        discussion.categories.set(category_ids)  # Set the many-to-many field using IDs
        return discussion

class DiscussionCommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = DiscussionComment
        fields = ['id', 'content', 'author_username', 'created_at', 'parent', 'replies']

    def get_replies(self, obj):
        if obj.replies.exists():
            return DiscussionCommentSerializer(obj.replies.all(), many=True).data
        return []
    
class DiscussionCommentExpandedSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()

    class Meta:
        model = DiscussionComment
        fields = ['id', 'content','post', 'author_username', 'created_at', 'parent', 'replies']

    def get_post(self, obj):
        return DiscussionSerializer(obj.post).data

    def get_replies(self, obj):
        if obj.replies.exists():
            return DiscussionCommentSerializer(obj.replies.all(), many=True).data
        return []

class DiscussionDetailSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    categories = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Discussion
        fields = ['id', 'title', 'content', 'author_username', 'categories', 'created_at', 'comments']

    def get_categories(self, obj):
        return [{'id': cat.id, 'name': cat.name} for cat in obj.categories.all()]
    
    def get_comments(self, obj):
        comments = obj.comments.filter(parent=None).order_by('-created_at') # More recent first
        return DiscussionCommentSerializer(comments, many=True).data