from rest_framework import serializers
from .models import *

class ResourceSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = ['id', 'title', 'content', 'link', 'author_username', 'categories', 'created_at',
                  'min_income_pc', 'max_income_pc', 'min_income_gross', 'max_income_gross', 'attachment']
        
    def get_categories(self, obj):
        if obj.categories == None:
            return []
        else:
            return [{'id': cat.id, 'name': cat.name} for cat in obj.categories.all()]
        
class BursarySerializer(ResourceSerializer):   
    level = serializers.ChoiceField(choices=Bursary.LEVEL_CHOICES)
    class Meta(ResourceSerializer.Meta):  
        model = Bursary  
        fields = ResourceSerializer.Meta.fields + ['deadline','level']

class ResourceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceCategory
        fields = ['id', 'name']

class ResourceCreateSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        queryset=ResourceCategory.objects.all(), 
        required=True, 
        many=True
    )
    link = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    attachment = serializers.FileField(required=False, allow_null=True)
    min_income_pc = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    max_income_pc = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    min_income_gross = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    max_income_gross = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    class Meta:
        model = Resource
        fields = ['title', 'content', 'link', 'categories', 'min_income_pc',
                  'max_income_pc', 'min_income_gross', 'max_income_gross', 'attachment']
        
class BursaryCreateSerializer(serializers.ModelSerializer):
    link = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    attachment = serializers.FileField(required=False, allow_null=True)
    min_income_pc = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    max_income_pc = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    min_income_gross = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    max_income_gross = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    deadline = serializers.DateField(required=False, allow_null=True)
    level = serializers.ChoiceField(choices=Bursary.LEVEL_CHOICES, required=True)
    

    class Meta(ResourceCreateSerializer.Meta):  
        model = Bursary  
        fields = [field for field in ResourceCreateSerializer.Meta.fields if field != "categories"] + ['deadline','level']

    def validate_deadline(self, value):
        if value == "":  # Convert empty string to None
            return None
        return value

class ResourceCommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = ResourceComment
        fields = ['id', 'content', 'author_username', 'created_at', 'parent', 'replies']

    def get_replies(self, obj):
        if obj.replies.exists():
            return ResourceCommentSerializer(obj.replies.all(), many=True).data
        return []
    
class ResourceCommentExpandedSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()

    class Meta:
        model = ResourceComment
        fields = ['id', 'content', 'author_username', 'created_at', 'parent', 'replies','post']

    def get_post(self, obj):
        return ResourceSerializer(obj.post).data

    def get_replies(self, obj):
        if obj.replies.exists():
            return ResourceCommentSerializer(obj.replies.all(), many=True).data
        return []

class ResourceDetailSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    categories = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()
    
    class Meta:
        model = Resource
        fields = [
            'id', 'title', 'content', 'link', 'author_username', 'categories', 'created_at', 'comments',
            'min_income_pc', 'max_income_pc', 'min_income_gross', 'max_income_gross', 'attachment'
        ]

    def get_comments(self, obj):
        comments = obj.comments.filter(parent=None).order_by('-created_at')
        return ResourceCommentSerializer(comments, many=True).data
    
    def get_categories(self, obj):
        return [{'id': cat.id, 'name': cat.name} for cat in obj.categories.all()]

    def get_attachment(self, obj):
        # Return full URL of the attachment if it exists
        request = self.context.get('request')
        if obj.attachment:
            return request.build_absolute_uri(obj.attachment.url)
        return None
    
class BursaryDetailSerializer(ResourceDetailSerializer):
    deadline = serializers.DateField()
    level = serializers.ChoiceField(choices=Bursary.LEVEL_CHOICES)

    class Meta(ResourceDetailSerializer.Meta):
        model = Bursary
        fields = [field for field in ResourceCreateSerializer.Meta.fields if field != "categories"] + ['deadline', 'level']

      
    