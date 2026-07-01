"""Application serializers for API."""

from rest_framework import serializers

from jobs.serializers import JobSummarySerializer
from users.serializers import UserSummarySerializer

from .models import Application, ApplicationNote, ApplicationStatusHistory


class ApplicationListSerializer(serializers.ModelSerializer):
    """Serializer for application list."""

    candidate_email = serializers.CharField(
        source='candidate.email', read_only=True
    )
    job_title = serializers.CharField(
        source='job.title', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )

    class Meta:
        model = Application
        fields = (
            'id',
            'candidate_email',
            'job_title',
            'status',
            'status_display',
            'rating',
            'created_at',
        )


class ApplicationNoteSerializer(serializers.ModelSerializer):
    """Serializer for application notes."""

    employer_email = serializers.CharField(source='employer.email', read_only=True)

    class Meta:
        model = ApplicationNote
        fields = ('id', 'note', 'employer_email', 'created_at', 'updated_at')


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for application status history."""

    old_status_display = serializers.CharField(
        source='get_old_status_display', read_only=True)
    new_status_display = serializers.CharField(
        source='get_new_status_display', read_only=True)
    changed_by_email = serializers.CharField(
        source='changed_by.email', read_only=True)

    class Meta:
        model = ApplicationStatusHistory
        fields = (
            'id',
            'old_status',
            'old_status_display',
            'new_status',
            'new_status_display',
            'changed_by_email',
            'changed_at',
            'reason')


class ApplicationDetailSerializer(serializers.ModelSerializer):
    """Serializer for application detail."""

    candidate = UserSummarySerializer(read_only=True)
    job = JobSummarySerializer(read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    employer_notes = ApplicationNoteSerializer(
        many=True, read_only=True
    )
    status_history = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = (
            'id',
            'candidate',
            'job',
            'resume',
            'cover_letter',
            'status',
            'status_display',
            'rating',
            'notes',
            'rejection_reason',
            'employer_notes',
            'status_history',
            'created_at',
            'updated_at',
        )

    def get_status_history(self, obj):
        """Required prefetch: status_history."""
        return ApplicationStatusHistorySerializer(
            obj.status_history.all(),
            many=True,
        ).data


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating applications."""

    job_id = serializers.CharField(write_only=True)
    resume = serializers.FileField()

    class Meta:
        model = Application
        fields = ('job_id', 'resume', 'cover_letter')

    def validate_resume(self, value):
        """Validate resume file."""
        from django.conf import settings

        if value.size > settings.MAX_RESUME_SIZE:
            size_mb = settings.MAX_RESUME_SIZE / (1024 * 1024)
            raise serializers.ValidationError(
                f"File size exceeds {size_mb:.1f}MB limit"
            )

        return value

    def create(self, validated_data):
        """Create application."""
        from jobs.models import Job

        user = self.context['request'].user
        job_id = validated_data.pop('job_id')

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            raise serializers.ValidationError({'job_id': 'Job not found.'})

        # Check if already applied
        if Application.objects.filter(candidate=user, job=job).exists():
            raise serializers.ValidationError('You have already applied to this job.')

        from .services import create_application

        return create_application(candidate=user, job=job, **validated_data)


class ApplicationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating application status."""

    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Application
        fields = ('status', 'status_display', 'rating', 'notes', 'rejection_reason')
