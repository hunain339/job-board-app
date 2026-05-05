"""User serializers for API."""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, EmailVerificationToken
import uuid

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile."""
    
    class Meta:
        model = UserProfile
        fields = (
            'skills', 'experience_years', 'headline',
            'social_github', 'social_linkedin', 'social_twitter'
        )


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed user information."""
    
    profile = UserProfileSerializer(read_only=True)
    role_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'role', 'role_display',
            'avatar', 'bio', 'phone_number', 'location', 'website',
            'company_name', 'company_description', 'company_website', 'company_logo',
            'is_approved_employer', 'profile', 'date_joined'
        )
    
    def get_role_display(self, obj):
        return obj.get_role_display()


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for user list view."""
    
    role_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'role', 'role_display',
            'avatar', 'company_name'
        )
    
    def get_role_display(self, obj):
        return obj.get_role_display()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    
    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'role',
            'password', 'password_confirm', 'phone_number', 'location'
        )
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs.get('password') != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs
    
    def validate_email(self, value):
        """Validate that email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value
    
    def create(self, validated_data):
        """Create new user with hashed password."""
        validated_data['username'] = validated_data['email']
        user = User.objects.create_user(**validated_data)
        
        # Generate verification token
        token = str(uuid.uuid4())
        EmailVerificationToken.objects.create(user=user, token=token)
        
        # In production, send verification email
        # send_verification_email.delay(user.id, token)
        
        return user


class EmployerRegistrationSerializer(UserRegistrationSerializer):
    """Extended serializer for employer registration."""
    
    company_name = serializers.CharField(required=True)
    company_description = serializers.CharField(required=False, allow_blank=True)
    
    class Meta(UserRegistrationSerializer.Meta):
        fields = UserRegistrationSerializer.Meta.fields + (
            'company_name', 'company_description'
        )
    
    def create(self, validated_data):
        """Create employer user."""
        user = super().create(validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""
    
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'avatar', 'bio',
            'phone_number', 'location', 'website',
            'company_name', 'company_description', 'company_website', 'company_logo'
        )


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs.get('new_password') != attrs.pop('new_password_confirm'):
            raise serializers.ValidationError({
                'new_password': 'Passwords do not match.'
            })
        return attrs


class EmployerApprovalSerializer(serializers.ModelSerializer):
    """Serializer for employer approval (admin only)."""
    
    class Meta:
        model = User
        fields = ('id', 'email', 'company_name', 'is_approved_employer', 'approval_status')
        read_only_fields = ('id', 'email', 'company_name')
