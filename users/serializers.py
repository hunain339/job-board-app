"""User serializers for API."""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import UserProfile
from .services import authenticate_with_email, issue_tokens_for_user, register_user

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


class UserSummarySerializer(serializers.ModelSerializer):
    """Compact serializer for nested user representations."""

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'avatar', 'location'
        )


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, min_length=12)
    password_confirm = serializers.CharField(write_only=True, min_length=12)

    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'role',
            'password', 'password_confirm', 'phone_number', 'location'
        )
        read_only_fields = ('role', 'is_staff', 'is_superuser')

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

    def validate_password(self, value):
        """Run Django's configured password validation pipeline."""
        validate_password(value)
        return value

    def create(self, validated_data):
        """Create new user through the service layer."""
        return register_user(user_model=User, **validated_data)


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
    new_password = serializers.CharField(write_only=True, min_length=12)
    new_password_confirm = serializers.CharField(write_only=True, min_length=12)

    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs.get('new_password') != attrs.pop('new_password_confirm'):
            raise serializers.ValidationError({
                'new_password': 'Passwords do not match.'
            })
        return attrs

    def validate_new_password(self, value):
        """Run Django's configured password validation pipeline."""
        validate_password(value)
        return value


class EmployerApprovalSerializer(serializers.ModelSerializer):
    """Serializer for employer approval (admin only)."""

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'company_name',
            'is_approved_employer',
            'approval_status')
        read_only_fields = ('id', 'email', 'company_name')


class EmailTokenObtainPairSerializer(serializers.Serializer):
    """Custom serializer for token obtain using email instead of username."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        request = self.context.get('request')
        user = authenticate_with_email(
            request=request,
            email=attrs.get('email'),
            password=attrs.get('password'),
        )
        return issue_tokens_for_user(user=user)
