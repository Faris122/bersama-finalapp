from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class RegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False, max_length=10)
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES, default='Public')

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'phone_number', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number', None)
        role = validated_data.pop('role', 'Public')
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, phone_number=phone_number, role=role)
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise serializers.ValidationError("Invalid username or password.")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
        else:
            raise serializers.ValidationError("Must include both username and password.")

        data['user'] = user
        return data
    
class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Profile
        fields = [
            'username', 'phone_number', 'is_phone_public', 'role', 
            'bio', 'profile_picture', 'website', 'is_dm_open', 'is_verified'
        ]

    def to_representation(self, instance):
        """Customize the representation of the serialized data."""
        representation = super().to_representation(instance)

        # Get the current user from the serializer context
        request = self.context.get('request')
        user = request.user if request else None

        # Check if the phone number should be hidden
        if not instance.is_phone_public and user != instance.user:
            representation.pop('phone_number', None)  # Remove the phone number for non-owners

        return representation
    
class ProfileEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone_number', 'is_phone_public', 'role', 'bio', 
                  'profile_picture', 'website', 'is_dm_open']
