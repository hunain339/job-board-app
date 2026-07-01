"""User views for API."""

from rest_framework import viewsets, status, filters, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

from core.permissions import IsAdminUser
from .serializers import (
    UserDetailSerializer, UserListSerializer, UserRegistrationSerializer,
    EmployerRegistrationSerializer, UserUpdateSerializer,
    PasswordChangeSerializer, EmployerApprovalSerializer,
    EmailTokenObtainPairSerializer
)
from .services import (
    approve_employer,
    authenticate_with_email,
    change_user_password,
    reject_employer,
    verify_user_email,
)


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management."""

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter]
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
        if self.action in [
            'create',
            'register_candidate',
            'register_employer',
                'verify_email']:
            return [AllowAny()]
        if self.action in ['retrieve', 'list']:
            return [IsAuthenticated()]
        if self.action in ['destroy', 'approve_employer']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = User.objects.select_related('profile')

        if user.role == 'admin':
            return queryset

        if user.role == 'employer':
            return queryset.filter(Q(role='candidate') | Q(pk=user.pk))

        return queryset.filter(Q(role='employer') | Q(pk=user.pk))

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

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def verify_email(self, request):
        """Verify email using token."""
        token = request.data.get('token')
        if not token:
            return Response({'detail': 'Token is required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        from .models import EmailVerificationToken
        try:
            verification_token = EmailVerificationToken.objects.get(
                token=token, is_used=False)
        except EmailVerificationToken.DoesNotExist:
            return Response({'detail': 'Invalid or expired token.'},
                            status=status.HTTP_400_BAD_REQUEST)

        verify_user_email(verification_token=verification_token)
        return Response({'detail': 'Email verified successfully.'})

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
            try:
                authenticate_with_email(
                    request=request,
                    email=request.user.email,
                    password=serializer.validated_data['old_password'],
                )
            except Exception:
                return Response(
                    {'detail': 'Invalid credentials.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            change_user_password(
                user=request.user,
                new_password=serializer.validated_data['new_password'],
            )
            return Response({'detail': 'Password changed successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Logout user and blacklist refresh token."""
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'detail': 'Refresh token is required.'},
                                status=status.HTTP_400_BAD_REQUEST)

            from rest_framework_simplejwt.tokens import RefreshToken
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Successfully logged out.'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
            approve_employer(user=user)
        elif action_type == 'reject':
            reject_employer(user=user)
        else:
            return Response(
                {'detail': 'Invalid action.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.refresh_from_db()
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


class EmailTokenObtainPairView(views.APIView):
    """Custom token view that accepts email and password."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Obtain JWT token using email and password."""
        serializer = EmailTokenObtainPairSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
