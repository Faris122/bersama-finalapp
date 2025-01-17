from rest_framework import serializers
from .models import *

class DiscussionSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    categories = serializers.StringRelatedField(many=True)

    class Meta:
        model = Discussion
        fields = ['id', 'title', 'content', 'author_username', 'categories', 'created_at']

class DiscussionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionCategory
        fields = ['id', 'name']

class DiscussionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discussion
        fields = ['title', 'content', 'categories']  # Exclude 'author' and 'created_at'

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

class DiscussionDetailSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    categories = serializers.StringRelatedField(many=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Discussion
        fields = ['id', 'title', 'content', 'author_username', 'categories', 'created_at', 'comments']

    def get_comments(self, obj):
        comments = obj.comments.filter(parent=None).order_by('-created_at')
        return DiscussionCommentSerializer(comments, many=True).data