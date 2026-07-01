"""Web views for jobs app."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView
from django.shortcuts import redirect

from .forms import JobPostForm
from .models import Job, JobCategory
from .services import JOB_CATEGORIES_WEB_CACHE_KEY


class JobListView(ListView):
    """Display all job listings."""

    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        location = self.request.GET.get('location', '')
        category_id = self.request.GET.get('category', '')
        job_type = self.request.GET.get('job_type', '')
        experience = self.request.GET.get('experience', '')
        is_remote = self.request.GET.get('is_remote', '')

        queryset = Job.objects.filter(
            is_active=True).select_related(
            'employer', 'category')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
            )

        if location:
            queryset = queryset.filter(location__icontains=location)

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if job_type:
            queryset = queryset.filter(job_type=job_type)

        if experience:
            queryset = queryset.filter(experience_level=experience)

        if is_remote == 'true':
            queryset = queryset.filter(is_remote=True)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = cache.get_or_set(
            JOB_CATEGORIES_WEB_CACHE_KEY,
            lambda: list(JobCategory.objects.order_by('name')),
            300,
        )
        return context


class JobDetailView(LoginRequiredMixin, DetailView):
    """Display job detail."""

    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('users_views:login')
    redirect_field_name = 'next'

    def get_queryset(self):
        return Job.objects.filter(is_active=True).select_related('employer', 'category')

    def get_object(self, queryset=None):
        job = super().get_object(queryset)
        Job.objects.filter(pk=job.pk).update(views_count=job.views_count + 1)
        job.views_count += 1
        return job

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.object
        related_cache_key = f'related_jobs_{job.category_id or "none"}'
        context['related_jobs'] = cache.get_or_set(
            related_cache_key,
            lambda: list(
                Job.objects.filter(
                    category=job.category,
                    is_active=True,
                )
                .exclude(id=job.id)
                .select_related('employer', 'category')[:5]
            ),
            300,
        )
        return context


class PostJobView(LoginRequiredMixin, FormView):
    """Post a new job."""

    template_name = 'jobs/post_job.html'
    form_class = JobPostForm
    success_url = reverse_lazy('users_views:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role != 'employer':
            messages.error(request, 'Only employers can post jobs.')
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        job = form.save(commit=False)
        job.employer = self.request.user
        job.save()
        messages.success(self.request, 'Job posted successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = cache.get_or_set(
            JOB_CATEGORIES_WEB_CACHE_KEY,
            lambda: list(JobCategory.objects.order_by('name')),
            300,
        )
        return context


class JobSearchView(ListView):
    """Search jobs."""

    template_name = 'jobs/job_search.html'
    context_object_name = 'jobs'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        location = self.request.GET.get('location', '')
        category_id = self.request.GET.get('category', '')
        job_type = self.request.GET.get('job_type', '')
        experience = self.request.GET.get('experience', '')
        is_remote = self.request.GET.get('is_remote', '')

        jobs = Job.objects.filter(is_active=True).select_related('employer', 'category')

        if query:
            jobs = jobs.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
            )

        if location:
            jobs = jobs.filter(location__icontains=location)

        if category_id:
            jobs = jobs.filter(category_id=category_id)

        if job_type:
            jobs = jobs.filter(job_type=job_type)

        if experience:
            jobs = jobs.filter(experience_level=experience)

        if is_remote == 'true':
            jobs = jobs.filter(is_remote=True)

        return jobs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['categories'] = cache.get_or_set(
            JOB_CATEGORIES_WEB_CACHE_KEY,
            lambda: list(JobCategory.objects.order_by('name')),
            300,
        )
        return context
