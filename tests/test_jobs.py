"""Tests for jobs app."""

import pytest

from rest_framework import status
from jobs.models import Job, JobCategory
from tests.conftest import EmployerFactory

pytestmark = pytest.mark.django_db


class TestJobPosting:
    """Test job posting functionality."""

    @pytest.fixture
    def category(self):
        """Create a job category."""
        return JobCategory.objects.create(
            name='Backend',
            slug='backend'
        )

    def test_create_job_as_employer(self, employer_client, category):
        """Test creating a job posting as employer."""
        data = {
            'title': 'Senior Python Developer',
            'description': (
                'We are looking for a senior Python developer with '
                '5+ years of experience.'
            ),
            'job_type': 'full_time',
            'category_id': category.id,
            'location': 'San Francisco, CA',
            'is_remote': False,
            'salary_min': 120000,
            'salary_max': 150000,
            'currency': 'USD',
            'experience_level': 'senior',
            'required_skills': 'Python, Django, PostgreSQL, Docker',
        }

        response = employer_client.post('/api/jobs/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Job.objects.filter(title='Senior Python Developer').exists()

    def test_non_employer_cannot_post(self, authenticated_client, category):
        """Test that non-employers cannot post jobs."""
        data = {
            'title': 'Test Job',
            'description': 'Test description' * 10,
            'job_type': 'full_time',
            'category_id': category.id,
            'location': 'Test Location',
            'experience_level': 'mid',
            'required_skills': 'Python',
        }

        response = authenticated_client.post('/api/jobs/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_job_list(self, api_client):
        """Test listing jobs."""
        # Create test jobs
        category = JobCategory.objects.create(name='Test', slug='test')
        employer = EmployerFactory()

        for i in range(5):
            Job.objects.create(
                title=f'Job {i}',
                description='Test description' * 10,
                job_type='full_time',
                category=category,
                location='Test Location',
                experience_level='mid',
                required_skills='Python',
                employer=employer,
                is_active=True,
            )

        response = api_client.get('/api/jobs/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 5

    def test_job_detail(self, api_client):
        """Test retrieving job detail."""
        category = JobCategory.objects.create(name='Test', slug='test')
        employer = EmployerFactory()
        job = Job.objects.create(
            title='Test Job',
            description='Test description' * 10,
            job_type='full_time',
            category=category,
            location='Test Location',
            experience_level='mid',
            required_skills='Python',
            employer=employer,
            is_active=True,
            slug='test-job',
        )

        response = api_client.get(f'/api/jobs/{job.slug}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Job'

        # Verify view count increased
        job.refresh_from_db()
        assert job.views_count == 1

    def test_save_job(self, authenticated_client):
        """Test saving a job."""

        category = JobCategory.objects.create(name='Test', slug='test')
        employer = EmployerFactory()
        job = Job.objects.create(
            title='Test Job',
            description='Test description' * 10,
            job_type='full_time',
            category=category,
            location='Test Location',
            experience_level='mid',
            required_skills='Python',
            employer=employer,
            is_active=True,
            slug='test-job',
        )

        response = authenticated_client.post(f'/api/jobs/{job.slug}/save/')
        assert response.status_code == status.HTTP_201_CREATED
