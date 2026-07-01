"""Tests for users web views."""

# bandit: skip-file

import pytest

from django.contrib.auth import get_user_model
from django.template.response import TemplateResponse

pytestmark = pytest.mark.django_db

User = get_user_model()


class TestUserWebViews:
    """Test user authentication and profile web views."""

    def test_register_view_renders_and_creates_user(self, client):
        """Test registration view success and invalid form handling."""
        response = client.get("/users/register/")
        assert response.status_code == 200
        assert response.templates[0].name == "auth/register.html"

        valid_data = {
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        valid_response = client.post("/users/register/candidate/", valid_data)
        assert valid_response.status_code == 302
        assert valid_response.url == "/users/login/"
        assert User.objects.filter(email="new@example.com").exists()

        invalid_response = client.post("/users/register/candidate/", {"email": ""})
        assert invalid_response.status_code == 200
        assert invalid_response.templates[0].name == "auth/register_candidate.html"
        assert invalid_response.context["form"].errors

    def test_login_view_redirects_authenticated_user_and_renders_form(
        self, client, user
    ):
        """Test login view for anonymous and authenticated users."""
        response = client.get("/users/login/")
        assert response.status_code == 200
        assert response.templates[0].name == "auth/login.html"

        user.set_password("StrongPass123!")
        user.save()

        client.force_login(user)
        authenticated_response = client.get("/users/login/")
        assert authenticated_response.status_code == 200
        assert authenticated_response.templates[0].name == "auth/login.html"

        client.logout()
        login_response = client.post(
            "/users/login/",
            {"email": user.email, "password": "StrongPass123!"},
        )
        assert login_response.status_code == 302
        assert login_response.url == "/users/dashboard/"

    def test_logout_view_logs_out_user(self, client, user):
        """Test logout view."""
        user.set_password("StrongPass123!")
        user.save()
        client.force_login(user)

        response = client.post("/users/logout/")
        assert response.status_code == 302
        assert response.url == "/"
        assert "_auth_user_id" not in client.session

    def test_profile_view_requires_matching_user(self, client, user):
        """Test profile view access control."""
        owner = user
        owner.set_password("StrongPass123!")
        owner.save()
        other = User.objects.create_user(
            email="other@example.com",
            username="other",
            password="StrongPass123!",
            role="candidate",
            is_active=True,
        )

        response = client.get(f"/users/profile/{owner.id}/")
        assert response.status_code == 200
        assert response.templates[0].name == "auth/profile.html"
        assert response.context["profile_user"] == owner

        client.force_login(other)
        other_response = client.get(f"/users/profile/{owner.id}/")
        assert other_response.status_code == 200
        assert other_response.context["profile_user"] == owner

        client.force_login(owner)
        allowed_response = client.get(f"/users/profile/{owner.id}/")
        assert allowed_response.status_code == 200
        assert allowed_response.templates[0].name == "auth/profile.html"
        assert isinstance(allowed_response, TemplateResponse)

    def test_dashboard_view_redirects_for_non_authenticated_users(self, client):
        """Test dashboard access control."""
        response = client.get("/users/dashboard/")
        assert response.status_code == 302
        assert response.url == "/users/login/?next=/users/dashboard/"

        user = User.objects.create_user(
            email="dashboard@example.com",
            username="dashboard",
            password="StrongPass123!",
            role="candidate",
            is_active=True,
        )
        client.force_login(user)
        authenticated_response = client.get("/users/dashboard/")
        assert authenticated_response.status_code == 200
        assert (
            authenticated_response.templates[0].name == "auth/dashboard_candidate.html"
        )
