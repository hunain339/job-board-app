#!/usr/bin/env python
"""
Create sample job categories, employer and job posts for testing.
Development only.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from jobs.models import Job, JobCategory
from django.utils.text import slugify
from django.utils import timezone

User = get_user_model()

SAMPLE_CATEGORIES = [
    'Engineering', 'Design', 'Product', 'Marketing', 'Sales'
]

SAMPLE_JOBS = [
    {
        'title': 'Senior Backend Engineer',
        'location': 'Remote',
        'job_type': 'full_time',
        'experience_level': 'senior',
        'is_remote': True,
        'salary_min': 90000,
        'salary_max': 140000,
        'required_skills': 'Python, Django, PostgreSQL, Docker',
        'description': (
            'Build and maintain scalable backend systems. '
            'Work closely with product and design.'
        ),
    },
    {
        'title': 'Product Designer',
        'location': 'New York, NY',
        'job_type': 'full_time',
        'experience_level': 'mid',
        'is_remote': False,
        'salary_min': 70000,
        'salary_max': 110000,
        'required_skills': 'Figma, UX, Prototyping',
        'description': (
            'Design delightful user experiences and collaborate '
            'with engineers.'
        ),
    },
    {
        'title': 'Growth Marketing Manager',
        'location': 'London, UK',
        'job_type': 'full_time',
        'experience_level': 'mid',
        'is_remote': True,
        'salary_min': 60000,
        'salary_max': 100000,
        'required_skills': 'SEO, Analytics, Content',
        'description': (
            'Lead growth experiments and own marketing funnels.'
        ),
    },
]


class Command(BaseCommand):
    help = 'Create sample job categories, employer and job posts (development only)'

    def handle(self, *args, **options):
        # create categories
        categories = {}
        for name in SAMPLE_CATEGORIES:
            cat, _ = JobCategory.objects.get_or_create(name=name)
            categories[name] = cat
            self.stdout.write(f"✓ Category: {name}")

        # create employer user
        employer_email = 'acme.hr@example.com'
        employer, created = User.objects.get_or_create(email=employer_email, defaults={
            'username': employer_email,
            'role': 'employer',
            'is_active': True,
        })
        if created:
            employer.set_password('EmployerPass123!')
            employer.company_name = 'Acme Corp'
            employer.company_description = (
                'Innovative company building useful products.'
            )
            employer.is_approved_employer = True
            employer.save()
            self.stdout.write(f"✓ Employer created: {employer_email}")
        else:
            self.stdout.write(f"✓ Employer exists: {employer_email}")

        # create sample jobs
        for i, data in enumerate(SAMPLE_JOBS, start=1):
            if i == 1:
                cat = categories.get('Engineering')
            elif i == 2:
                cat = categories.get('Design')
            else:
                cat = categories.get('Marketing')
            slug = slugify(f"{data['title']}-{i}")
            job, created = Job.objects.get_or_create(
                title=data['title'],
                defaults={
                    'slug': slug,
                    'location': data['location'],
                    'job_type': data['job_type'],
                    'experience_level': data['experience_level'],
                    'is_remote': data['is_remote'],
                    'salary_min': data['salary_min'],
                    'salary_max': data['salary_max'],
                    'required_skills': data['required_skills'],
                    'description': data['description'],
                    'employer': employer,
                    'category': cat,
                    'is_active': True,
                    'created_at': timezone.now(),
                }
            )
            if created:
                self.stdout.write(f"✓ Created job: {job.title}")
            else:
                self.stdout.write(f"✓ Job exists: {job.title}")

        self.stdout.write(self.style.SUCCESS('\nSample jobs created/verified.'))
