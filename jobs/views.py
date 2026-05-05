"""Job views for API."""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Job, JobCategory, JobSavedByUser
from .serializers import (
    JobListSerializer, JobDetailSerializer, JobCreateUpdateSerializer,
    JobCategorySerializer, JobSavedByUserSerializer
)
from core.permissions import IsEmployer, IsApprovedEmployer, IsEmployerOwner


class JobCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for job categories."""
    
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class JobViewSet(viewsets.ModelViewSet):
    """ViewSet for job postings."""
    
    queryset = Job.objects.filter(is_active=True)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['job_type', 'experience_level', 'is_remote', 'is_featured', 'category']
    search_fields = ['title', 'description', 'required_skills', 'location', 'employer__company_name']
    ordering_fields = ['created_at', 'salary_min', 'applications_count', 'views_count']
    ordering = ['-created_at']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return JobListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return JobCreateUpdateSerializer
        return JobDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action == 'create':
            return [IsApprovedEmployer()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter queryset."""
        queryset = Job.objects.all()
        
        # Non-authenticated users see only active jobs
        if not self.request.user.is_authenticated:
            return queryset.filter(is_active=True)
        
        # Employers see their own jobs (active or not) + all active jobs
        if self.request.user.role == 'employer':
            return queryset.filter(
                Q(is_active=True) | Q(employer=self.request.user)
            )
        
        return queryset.filter(is_active=True)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve job and increment view count."""
        job = self.get_object()
        job.views_count += 1
        job.save(update_fields=['views_count'])
        
        return super().retrieve(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Create job with current user as employer."""
        serializer.save(employer=self.request.user)
    
    def perform_update(self, serializer):
        """Update job if user is employer."""
        job = self.get_object()
        if job.employer != self.request.user:
            self.permission_denied(self.request)
        serializer.save()
    
    def perform_destroy(self, instance):
        """Soft delete job."""
        if instance.employer != self.request.user:
            self.permission_denied(self.request)
        instance.is_active = False
        instance.save()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def save(self, request, slug=None):
        """Save job for later."""
        job = self.get_object()
        
        if request.user.role != 'candidate':
            return Response(
                {'detail': 'Only candidates can save jobs.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        saved, created = JobSavedByUser.objects.get_or_create(
            candidate=request.user,
            job=job
        )
        
        if created:
            return Response(
                {'detail': 'Job saved successfully.'},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'detail': 'Job already saved.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unsave(self, request, slug=None):
        """Unsave job."""
        job = self.get_object()
        
        if request.user.role != 'candidate':
            return Response(
                {'detail': 'Only candidates can unsave jobs.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        deleted_count, _ = JobSavedByUser.objects.filter(
            candidate=request.user,
            job=job
        ).delete()
        
        if deleted_count > 0:
            return Response({'detail': 'Job removed from saved.'})
        return Response(
            {'detail': 'Job was not saved.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_jobs(self, request):
        """Get jobs posted by current employer."""
        if request.user.role != 'employer':
            return Response(
                {'detail': 'Only employers can view their jobs.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = Job.objects.filter(employer=request.user).order_by('-created_at')
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = JobDetailSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = JobDetailSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def saved(self, request):
        """Get saved jobs for candidate."""
        if request.user.role != 'candidate':
            return Response(
                {'detail': 'Only candidates can view saved jobs.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        saved_jobs = JobSavedByUser.objects.filter(candidate=request.user).order_by('-created_at')
        page = self.paginate_queryset(saved_jobs)
        
        if page is not None:
            serializer = JobSavedByUserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JobSavedByUserSerializer(saved_jobs, many=True)
        return Response(serializer.data)
