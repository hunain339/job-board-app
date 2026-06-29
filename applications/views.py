"""Application views for API."""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch

from .models import Application, ApplicationNote, ApplicationStatusHistory
from .serializers import (
    ApplicationListSerializer, ApplicationDetailSerializer,
    ApplicationCreateSerializer, ApplicationUpdateSerializer,
    ApplicationNoteSerializer
)
from .services import add_application_note, update_application_status, withdraw_application


class ApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for job applications."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'job', 'candidate']
    search_fields = ['candidate__email', 'job__title']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ApplicationListSerializer
        elif self.action == 'create':
            return ApplicationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ApplicationUpdateSerializer
        return ApplicationDetailSerializer

    def get_queryset(self):
        """Filter applications with optimized queries to prevent N+1."""
        user = self.request.user

        # Use select_related and prefetch_related to prevent N+1 queries

        # Prefetch related notes and history with their related objects
        notes_queryset = (
            ApplicationNote.objects.select_related('employer')
            .all()
        )

        history_queryset = (
            ApplicationStatusHistory.objects
            .select_related('changed_by')
            .all()
        )

        queryset = (
            Application.objects
            .select_related('candidate', 'job', 'job__employer', 'job__category')
            .prefetch_related(
                Prefetch('employer_notes', queryset=notes_queryset),
                # Required prefetch: status_history
                Prefetch('status_history', queryset=history_queryset)
            )
        )

        if user.role == 'candidate':
            return queryset.filter(candidate=user)
        elif user.role == 'employer':
            return queryset.filter(job__employer=user)
        elif user.role == 'admin':
            return queryset

        return queryset.none()

    def create(self, request, *args, **kwargs):
        """Create a new application."""
        if request.user.role != 'candidate':
            return Response(
                {'detail': 'Only candidates can apply to jobs.'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Update application - only employer can update status."""
        application = self.get_object()

        if request.user != application.job.employer:
            return Response(
                {'detail': 'Only the job employer can update application status.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(application, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        update_application_status(
            application=application,
            changed_by=request.user,
            reason=request.data.get('reason', ''),
            **serializer.validated_data,
        )
        application.refresh_from_db()
        return Response(ApplicationDetailSerializer(application, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_note(self, request, pk=None):
        """Add note to application (employer only)."""
        application = self.get_object()

        if request.user != application.job.employer:
            return Response(
                {'detail': 'Only the job employer can add notes.'},
                status=status.HTTP_403_FORBIDDEN
            )

        note_text = request.data.get('note', '')
        if not note_text:
            return Response(
                {'detail': 'Note text is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        note = add_application_note(
            application=application,
            employer=request.user,
            note=note_text,
        )

        serializer = ApplicationNoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_applications(self, request):
        """Get candidate's applications."""
        if request.user.role != 'candidate':
            return Response(
                {'detail': 'Only candidates can view their applications.'},
                status=status.HTTP_403_FORBIDDEN
            )

        applications = Application.objects.select_related('candidate', 'job', 'job__employer', 'job__category').filter(candidate=request.user)
        page = self.paginate_queryset(applications)

        if page is not None:
            serializer = ApplicationDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ApplicationDetailSerializer(applications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def job_applications(self, request):
        """Get applications for employer's jobs."""
        if request.user.role != 'employer':
            return Response(
                {'detail': 'Only employers can view job applications.'},
                status=status.HTTP_403_FORBIDDEN
            )

        applications = Application.objects.select_related('candidate', 'job', 'job__employer', 'job__category').filter(job__employer=request.user)

        # Filter by status if provided
        status_filter = request.query_params.get('status', None)
        if status_filter:
            applications = applications.filter(status=status_filter)

        page = self.paginate_queryset(applications)

        if page is not None:
            serializer = ApplicationDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ApplicationDetailSerializer(applications, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def withdraw(self, request, pk=None):
        """Withdraw application (candidate only)."""
        application = self.get_object()

        if request.user != application.candidate:
            return Response(
                {'detail': 'You can only withdraw your own applications.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if application.status in ['hired', 'rejected']:
            return Response(
                {'detail': f'Cannot withdraw application with status {application.get_status_display()}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        withdraw_application(application=application)
        return Response({'detail': 'Application withdrawn successfully.'})
