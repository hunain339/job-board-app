"""Web views for jobs app."""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Job, JobCategory
from django.core.paginator import Paginator
from .forms import JobPostForm
from django.contrib import messages
from django.urls import reverse_lazy


class JobListView(TemplateView):
    """Display all job listings."""
    template_name = 'jobs/job_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        jobs = Job.objects.filter(is_active=True).select_related('employer', 'category')
        
        # Pagination
        paginator = Paginator(jobs, 20)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context['page_obj'] = page_obj
        context['jobs'] = page_obj.object_list
        context['categories'] = JobCategory.objects.all()
        return context


class JobDetailView(TemplateView):
    """Display job detail."""
    template_name = 'jobs/job_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = get_object_or_404(Job, slug=kwargs.get('slug'), is_active=True)
        
        # Increment view count
        job.views_count += 1
        job.save(update_fields=['views_count'])
        
        context['job'] = job
        context['related_jobs'] = Job.objects.filter(
            category=job.category,
            is_active=True
        ).exclude(id=job.id)[:5]
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
        context['categories'] = JobCategory.objects.all()
        return context


class JobSearchView(TemplateView):
    """Search jobs."""
    template_name = 'jobs/job_search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        job_type = self.request.GET.get('job_type', '')
        experience = self.request.GET.get('experience', '')
        is_remote = self.request.GET.get('is_remote', '')
        
        jobs = Job.objects.filter(is_active=True)
        
        if query:
            jobs = jobs.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query)
            )
        
        if job_type:
            jobs = jobs.filter(job_type=job_type)
        
        if experience:
            jobs = jobs.filter(experience_level=experience)
        
        if is_remote == 'true':
            jobs = jobs.filter(is_remote=True)
        
        # Pagination
        paginator = Paginator(jobs, 20)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context['page_obj'] = page_obj
        context['jobs'] = page_obj.object_list
        context['query'] = query
        context['categories'] = JobCategory.objects.all()
        return context
