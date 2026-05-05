"""User views for API."""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from core.permissions import IsApprovedEmployer, IsAdminUser
from .serializers import (
    UserDetailSerializer, UserListSerializer, UserRegistrationSerializer,
    EmployerRegistrationSerializer, UserUpdateSerializer,
    PasswordChangeSerializer, EmployerApprovalSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management."""
    
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'is_approved_employer']
    search_fields = ['email', 'first_name', 'last_name', 'company_name']
    ordering_fields = ['date_joined', 'email']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserRegistrationSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        return UserDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action == 'create':
            return [AllowAny()]
        if self.action in ['retrieve', 'list']:
            return [IsAuthenticated()]
        if self.action in ['destroy', 'approve_employer']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        
        if user.role == 'admin':
            return User.objects.all()
        
        # Non-admin users can only see themselves and employers
        if user.role == 'employer':
            return User.objects.filter(role__in=['employer', 'candidate'])
        
        # Candidates can see employers and other candidates
        return User.objects.filter(role__in=['employer', 'candidate'])
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register_candidate(self, request):
        """Register as a candidate."""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['role'] = 'candidate'
            user = serializer.save()
            return Response(
                UserDetailSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register_employer(self, request):
        """Register as an employer."""
        serializer = EmployerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['role'] = 'employer'
            user = serializer.save()
            return Response(
                UserDetailSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user details."""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Change user password."""
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': 'Incorrect password.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'detail': 'Password changed successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAdminUser],
        serializer_class=EmployerApprovalSerializer
    )
    def approve_employer(self, request, pk=None):
        """Approve an employer account (admin only)."""
        user = self.get_object()
        if user.role != 'employer':
            return Response(
                {'detail': 'User is not an employer.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        action_type = request.data.get('action', 'approve')
        
        if action_type == 'approve':
            user.is_approved_employer = True
            user.approval_status = 'approved'
            user.is_active = True
        elif action_type == 'reject':
            user.is_approved_employer = False
            user.approval_status = 'rejected'
        else:
            return Response(
                {'detail': 'Invalid action.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.save()
        return Response(UserDetailSerializer(user).data)
    
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAdminUser],
        queryset=User.objects.filter(role='employer', approval_status='pending')
    )
    def pending_employers(self, request):
        """List pending employer approvals (admin only)."""
        queryset = User.objects.filter(role='employer', approval_status='pending')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserDetailSerializer(queryset, many=True)
        return Response(serializer.data)
