from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class RegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False, max_length=10)
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES, default='Public')
    needs_help = serializers.BooleanField(required=False, default=False)
    bio = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.ImageField(required=False)
    website = serializers.CharField(required=False, allow_blank=True)
    is_dm_open = serializers.BooleanField(required=False, default=True)
    is_phone_public = serializers.BooleanField(required=False, default=True)

    # Financial Profile Fields (Only needed if needs_help=True)
    own_income = serializers.DecimalField(required=False, max_digits=10, decimal_places=2, allow_null=True)
    household_income = serializers.DecimalField(required=False, max_digits=10, decimal_places=2, allow_null=True)
    household_members = serializers.IntegerField(required=False, allow_null=True)
    employment_status = serializers.ChoiceField(
        choices=FinancialProfile.EMPLOYMENT_STATUS_CHOICES, required=False, allow_blank=True
    )
    housing_status = serializers.ChoiceField(
        choices=FinancialProfile.HOUSING_STATUS_CHOICES, required=False, allow_blank=True
    )

    class Meta:
        model = User
        fields = [
            'username', 'password', 'email', 'phone_number', 'role', 'needs_help',
            'bio', 'profile_picture', 'website', 'is_dm_open', 'is_phone_public',
            'own_income', 'household_income', 'household_members',
            'employment_status', 'housing_status'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        """
        Ensures that:
        1. Only Public users can request help.
        2. If `needs_help=True`, financial profile fields must be filled.
        """
        if data.get("needs_help", False) and data.get("role") != "Public":
            raise serializers.ValidationError("Only Public users can request help.")

        return data

    def create(self, validated_data):
        """
        Creates a User, associated Profile, and FinancialProfile (if needed).
        """
        # Extract financial data
        financial_data = {
            'own_income': validated_data.pop('own_income', None),
            'household_income': validated_data.pop('household_income', None),
            'household_members': validated_data.pop('household_members', None),
            'employment_status': validated_data.pop('employment_status', None),
            'housing_status': validated_data.pop('housing_status', None),
        }

        # Extract profile data
        profile_data = {
            'phone_number': validated_data.pop('phone_number', None),
            'role': validated_data.pop('role', 'Public'),
            'needs_help': validated_data.pop('needs_help', False),
            'bio': validated_data.pop('bio', ''),
            'profile_picture': validated_data.pop('profile_picture', None),
            'website': validated_data.pop('website', ''),
            'is_dm_open': validated_data.pop('is_dm_open', True),
            'is_phone_public': validated_data.pop('is_phone_public', True)
        }

        # Create User
        user = User.objects.create_user(**validated_data)
        profile = Profile.objects.create(user=user, **profile_data)

        # Create Financial Profile if user needs help
        if profile.needs_help:
            FinancialProfile.objects.create(profile=profile, **financial_data)

        return user

    def update(self, instance, validated_data):
        """
        Updates a User, Profile, and FinancialProfile.
        """
        profile = instance.profile  # Get associated profile

        # Update Profile fields
        profile.phone_number = validated_data.get('phone_number', profile.phone_number)
        profile.role = validated_data.get('role', profile.role)
        profile.needs_help = validated_data.get('needs_help', profile.needs_help)
        profile.bio = validated_data.get('bio', profile.bio)
        profile.profile_picture = validated_data.get('profile_picture', profile.profile_picture)
        profile.website = validated_data.get('website', profile.website)
        profile.is_dm_open = validated_data.get('is_dm_open', profile.is_dm_open)
        profile.is_phone_public = validated_data.get('is_phone_public', profile.is_phone_public)

        # Update Financial Profile if needed
        if profile.needs_help:
            financial_profile, _ = FinancialProfile.objects.get_or_create(profile=profile)
            financial_profile.own_income = validated_data.get('own_income', financial_profile.own_income)
            financial_profile.household_income = validated_data.get('household_income', financial_profile.household_income)
            financial_profile.household_members = validated_data.get('household_members', financial_profile.household_members)
            financial_profile.employment_status = validated_data.get('employment_status', financial_profile.employment_status)
            financial_profile.housing_status = validated_data.get('housing_status', financial_profile.housing_status)
            financial_profile.save()

        profile.save()
        return instance


    
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
            'bio', 'profile_picture', 'website', 'is_dm_open', 'needs_help'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        request = self.context.get('request')
        user = request.user if request else None

        if not instance.is_phone_public and user != instance.user:
            representation.pop('phone_number', None)

        return representation
    
class ProfileEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone_number', 'is_phone_public', 'role', 'bio', 
                  'profile_picture', 'website', 'is_dm_open']


class FinancialProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialProfile
        fields = '__all__'
        read_only_fields = ['profile']

    def validate(self, data):
        """
        Ensures:
        - Only public users can set `needs_help = True`
        - Only the owner can modify their financial profile
        """
        request = self.context.get('request')
        user = self.context['request'].user

        # Prevent organisations from marking themselves as needing help
        if data.get("needs_help", False) and user.profile.role != "Public":
            raise serializers.ValidationError("Only Public users can request help.")

        # Prevent users from modifying someone else's profile
        if self.instance and self.instance.profile.user != user:
            raise serializers.ValidationError("You can only edit your own financial profile.")

        return data

    def to_representation(self, instance):
        """
        - Users can see their own financial profile
        - Organisations can see all profiles
        - Others get restricted access
        """
        request = self.context.get('request')
        user = request.user
        data = super().to_representation(instance)

        # If the user is not the owner or an organisation, restrict sensitive fields
        if user != instance.profile.user and user.profile.role != "Organisation":
            restricted_fields = [
                'own_income', 'household_income', 'household_members',
                'monthly_expenses', 'has_elderly', 'has_children'
            ]
            for field in restricted_fields:
                data[field] = "Restricted"

        return data


