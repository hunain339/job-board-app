"""Tests for users app."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from users.models import User

pytestmark = pytest.mark.django_db


class TestUserRegistration:
    """Test user registration."""
    
    def test_candidate_registration(self, api_client):
        """Test candidate registration."""
        data = {
            'email': 'candidate@test.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123',
            'first_name': 'John',
            'last_name': 'Doe',
        }
        
        response = api_client.post('/api/users/register_candidate/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email='candidate@test.com').exists()
    
    def test_employer_registration(self, api_client):
        """Test employer registration."""
        data = {
            'email': 'employer@test.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'company_name': 'Tech Corp',
            'company_description': 'A tech company',
        }
        
        response = api_client.post('/api/users/register_employer/', data)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_registration_privilege_escalation(self, api_client):
        """Test that users cannot set role=admin or is_staff=True during registration."""
        data = {
            'email': 'hacker@test.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        }
        
        response = api_client.post('/api/users/register_candidate/', data)
        assert response.status_code == status.HTTP_201_CREATED
        
        user = User.objects.get(email='hacker@test.com')
        assert user.role == 'candidate'  # Should be forced to endpoint default
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_password_mismatch(self, api_client):
        """Test password mismatch validation."""
        data = {
            'email': 'test@test.com',
            'password': 'testpassword123',
            'password_confirm': 'differentpassword',
        }
        
        response = api_client.post('/api/users/register_candidate/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_duplicate_email(self, api_client, user):
        """Test duplicate email validation."""
        data = {
            'email': user.email,
            'password': 'testpassword123',
            'password_confirm': 'testpassword123',
        }
        
        response = api_client.post('/api/users/register_candidate/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestUserProfile:
    """Test user profile."""
    
    def test_get_current_user(self, authenticated_client, user):
        """Test retrieving current user profile."""
        response = authenticated_client.get('/api/users/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
    
    def test_change_password(self, authenticated_client, user):
        """Test changing password."""
        data = {
            'old_password': 'testpassword123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123',
        }
        
        response = authenticated_client.post('/api/users/change_password/', data)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify new password works
        user.refresh_from_db()
        assert user.check_password('newpassword123')

    def test_profile_update_privilege_escalation(self, authenticated_client, user):
        """Test that users cannot update their role or staff status via profile update."""
        original_role = user.role
        data = {
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
            'first_name': 'Hacked'
        }
        
        response = authenticated_client.patch(f'/api/users/{user.id}/', data)
        assert response.status_code in (status.HTTP_200_OK, status.HTTP_202_ACCEPTED)
        
        user.refresh_from_db()
        assert user.role == original_role
        assert user.first_name == 'Hacked'  # Ensuring the valid update went through
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_candidate_requires_verification(self, api_client):
        """Test new candidate cannot authenticate until verified."""
        data = {
            'email': 'unverified@test.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123',
            'first_name': 'John',
        }
        api_client.post('/api/users/register_candidate/', data)
        
        login_data = {'email': 'unverified@test.com', 'password': 'testpassword123'}
        # Assuming JWT is configured
        response = api_client.post('/api/token/', login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Verify
        from users.models import EmailVerificationToken
        token = EmailVerificationToken.objects.get(user__email='unverified@test.com').token
        api_client.post('/api/users/verify_email/', {'token': token})
        
        response = api_client.post('/api/token/', login_data)
        assert response.status_code == status.HTTP_200_OK

    def test_employer_requires_approval(self, api_client):
        """Test new employer cannot authenticate until verified AND approved."""
        data = {
            'email': 'unapproved@employer.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123',
            'company_name': 'Acme Corp',
        }
        api_client.post('/api/users/register_employer/', data)
        
        login_data = {'email': 'unapproved@employer.com', 'password': 'testpassword123'}
        response = api_client.post('/api/token/', login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_blacklisted_on_logout(self, authenticated_client, user):
        """Test that refresh token is blacklisted on logout."""
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        # Logout
        response = authenticated_client.post('/api/users/logout/', {'refresh': str(refresh)})
        assert response.status_code == status.HTTP_200_OK
        
        # Try to use refresh token again to get a new access token
        from rest_framework.test import APIClient
        anon_client = APIClient()
        refresh_response = anon_client.post('/api/token/refresh/', {'refresh': str(refresh)})
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED
