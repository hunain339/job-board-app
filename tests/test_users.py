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
