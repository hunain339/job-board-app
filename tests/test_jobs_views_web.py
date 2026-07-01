"""Tests for jobs web views."""

# bandit: skip-file

import pytest

from django.contrib.auth import get_user_model
from django.template.response import TemplateResponse
from jobs.models import Job, JobCategory

pytestmark = pytest.mark.django_db

User = get_user_model()


class TestJobWebViews:
    """Test job listing and posting web views."""

    @pytest.fixture
    def category(self):
        """Create a job category."""
        return JobCategory.objects.create(name="Backend", slug="backend")

    def test_job_list_renders_and_filters_jobs(self, client, employer, category):
        """Test listing jobs with query filters."""
        Job.objects.create(
            title="Python Developer",
            description="Python role",
            job_type="full_time",
            category=category,
            location="Remote",
            experience_level="mid",
            required_skills="Python",
            is_remote=True,
            employer=employer,
            is_active=True,
            slug="python-developer",
        )
        Job.objects.create(
            title="Design Role",
            description="Design role",
            job_type="full_time",
            category=category,
            location="Remote",
            experience_level="mid",
            required_skills="Figma",
            employer=employer,
            is_active=True,
            slug="design-role",
        )
        Job.objects.create(
            title="Archived Role",
            description="Not visible",
            job_type="full_time",
            category=category,
            location="Remote",
            experience_level="mid",
            required_skills="Python",
            employer=employer,
            is_active=False,
            slug="archived-role",
        )

        response = client.get(
            "/",
            {
                "q": "Python",
                "location": "Remote",
                "category": str(category.id),
                "job_type": "full_time",
                "experience": "mid",
                "is_remote": "true",
            },
        )

        assert response.status_code == 200
        assert isinstance(response, TemplateResponse)
        assert response.templates[0].name == "jobs/job_list.html"
        assert response.context["jobs"].count() == 1
        assert response.context["categories"]

    def test_job_detail_requires_login_and_updates_views_count(
        self, client, employer, category
    ):
        """Test job detail access and view count updates."""
        job = Job.objects.create(
            title="Test Job",
            description="Test description",
            job_type="full_time",
            category=category,
            location="Test Location",
            experience_level="mid",
            required_skills="Python",
            employer=employer,
            is_active=True,
            slug="test-job",
        )

        unauthenticated_response = client.get(f"/job/{job.slug}/")
        assert unauthenticated_response.status_code == 302
        assert unauthenticated_response.url == f"/users/login/?next=/job/{job.slug}/"

        client.force_login(employer)
        response = client.get(f"/job/{job.slug}/")
        assert response.status_code == 200
        assert response.templates[0].name == "jobs/job_detail.html"

        job.refresh_from_db()
        assert job.views_count == 1

    def test_post_job_view_redirects_non_employer_and_renders_form(
        self, client, user, employer, category
    ):
        """Test employer-only posting flow and invalid form handling."""
        client.force_login(user)
        response = client.get("/post/")
        assert response.status_code == 302
        assert response.url == "/"

        client.logout()
        unauthenticated_response = client.get("/post/")
        assert unauthenticated_response.status_code == 302
        assert unauthenticated_response.url == "/users/login/?next=/post/"

        client.logout()
        client.force_login(employer)
        employer_response = client.get("/post/")
        assert employer_response.status_code == 200
        assert employer_response.templates[0].name == "jobs/post_job.html"
        assert employer_response.context["categories"]

        valid_data = {
            "title": "Senior Python Developer",
            "description": "We need a senior Django developer.",
            "job_type": "full_time",
            "experience_level": "senior",
            "location": "Berlin",
            "is_remote": True,
            "salary_min": 120000,
            "salary_max": 150000,
            "required_skills": "Python, Django",
            "category": category.id,
        }
        valid_response = client.post("/post/", valid_data)
        assert valid_response.status_code == 302
        assert valid_response.url == "/users/dashboard/"
        assert Job.objects.filter(title="Senior Python Developer").exists()

        invalid_response = client.post("/post/", {"title": ""})
        assert invalid_response.status_code == 200
        assert invalid_response.templates[0].name == "jobs/post_job.html"
        assert invalid_response.context["form"].errors

    def test_job_search_renders_search_results(self, client, employer, category):
        """Test job search view."""
        Job.objects.create(
            title="Python Search Result",
            description="Find me",
            job_type="full_time",
            category=category,
            location="Remote",
            experience_level="mid",
            required_skills="Python",
            employer=employer,
            is_active=True,
            slug="python-search-result",
        )

        response = client.get("/search/", {"q": "Python"})
        assert response.status_code == 200
        assert response.templates[0].name == "jobs/job_search.html"
        assert response.context["query"] == "Python"
        assert response.context["jobs"].count() == 1
