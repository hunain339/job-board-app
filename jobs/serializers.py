"""Job serializers for API."""

from rest_framework import serializers
from .models import Job, JobCategory, JobSavedByUser


class JobCategorySerializer(serializers.ModelSerializer):
    """Serializer for JobCategory."""

    class Meta:
        model = JobCategory
        fields = ('id', 'name', 'slug', 'description', 'icon')


class JobListSerializer(serializers.ModelSerializer):
    """Serializer for job list view."""

    employer_email = serializers.CharField(source='employer.email', read_only=True)
    employer_company = serializers.CharField(
        source='employer.company_name', read_only=True)
    job_type_display = serializers.CharField(
        source='get_job_type_display', read_only=True)
    experience_display = serializers.CharField(
        source='get_experience_level_display', read_only=True)
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = (
            'id',
            'title',
            'slug',
            'job_type',
            'job_type_display',
            'location',
            'is_remote',
            'salary_min',
            'salary_max',
            'currency',
            'experience_level',
            'experience_display',
            'employer_email',
            'employer_company',
            'created_at',
            'is_featured',
            'views_count',
            'applications_count',
            'is_saved')

    def get_is_saved(self, obj):
        """Check if job is saved by current user."""
        annotated = getattr(obj, 'is_saved', None)
        if annotated is not None:
            return bool(annotated)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return JobSavedByUser.objects.filter(
                candidate=request.user, job=obj
            ).exists()
        return False


class JobDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed job view."""

    category = JobCategorySerializer(read_only=True)
    employer_email = serializers.CharField(source='employer.email', read_only=True)
    employer_company = serializers.CharField(
        source='employer.company_name', read_only=True)
    employer_logo = serializers.ImageField(
        source='employer.company_logo', read_only=True)
    job_type_display = serializers.CharField(
        source='get_job_type_display', read_only=True)
    experience_display = serializers.CharField(
        source='get_experience_level_display', read_only=True)
    is_saved = serializers.SerializerMethodField()
    applications = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = (
            'id', 'title', 'slug', 'description', 'job_type', 'job_type_display',
            'category', 'location', 'is_remote', 'salary_min', 'salary_max', 'currency',
            'experience_level', 'experience_display', 'required_skills',
            'employer_email', 'employer_company', 'employer_logo',
            'is_active', 'is_featured', 'views_count', 'applications_count',
            'is_saved', 'applications', 'created_at', 'updated_at'
        )

    def get_is_saved(self, obj):
        """Check if job is saved by current user."""
        annotated = getattr(obj, 'is_saved', None)
        if annotated is not None:
            return bool(annotated)
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == 'candidate':
            return JobSavedByUser.objects.filter(
                candidate=request.user, job=obj
            ).exists()
        return False

    def get_applications(self, obj):
        """Get application count (for employer only)."""
        request = self.context.get('request')
        if request and request.user == obj.employer:
            return obj.applications_count
        return None


class JobSummarySerializer(serializers.ModelSerializer):
    """Compact serializer for nested job representations."""

    class Meta:
        model = Job
        fields = ('id', 'title', 'slug', 'location')


class JobCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating jobs."""

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=JobCategory.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Job
        fields = (
            'title', 'description', 'job_type', 'category_id',
            'location', 'is_remote', 'salary_min', 'salary_max', 'currency',
            'experience_level', 'required_skills', 'is_featured'
        )

    def validate_title(self, value):
        """Validate job title."""
        if len(value) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters.")
        return value

    def validate_description(self, value):
        """Validate job description."""
        if len(value) < 50:
            raise serializers.ValidationError(
                "Description must be at least 50 characters.")
        return value


class JobSavedByUserSerializer(serializers.ModelSerializer):
    """Serializer for saved jobs."""

    job = JobListSerializer(read_only=True)

    class Meta:
        model = JobSavedByUser
        fields = ('id', 'job', 'created_at')
