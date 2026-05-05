"""Web views for applications app."""

from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from .models import Application
from jobs.models import Job


from django.views import View
from django.shortcuts import redirect
from django.contrib import messages


class MyApplicationsView(LoginRequiredMixin, TemplateView):
    """View candidate's applications."""
    template_name = 'applications/my_applications.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.role != 'candidate':
            context['error'] = 'Only candidates can view applications.'
            return context
        
        applications = Application.objects.filter(
            candidate=self.request.user
        ).select_related('job', 'job__employer')
        
        # Pagination
        paginator = Paginator(applications, 10)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context['page_obj'] = page_obj
        context['applications'] = page_obj.object_list
        return context


class JobApplicationsView(LoginRequiredMixin, TemplateView):
    """View applications for a job (employer only)."""
    template_name = 'applications/job_applications.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.role != 'employer':
            context['error'] = 'Only employers can view applications.'
            return context
        
        job = get_object_or_404(Job, id=kwargs.get('job_id'))
        
        if job.employer != self.request.user:
            context['error'] = 'You do not have permission to view these applications.'
            return context
        
        applications = Application.objects.filter(job=job).select_related('candidate')
        
        # Filter by status
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            applications = applications.filter(status=status_filter)
        
        # Pagination
        paginator = Paginator(applications, 10)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context['page_obj'] = page_obj
        context['applications'] = page_obj.object_list
        context['job'] = job
        context['status_choices'] = Application.STATUS_CHOICES
        return context


class ApplicationDetailView(LoginRequiredMixin, TemplateView):
    """View application detail."""
    template_name = 'applications/application_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = get_object_or_404(Application, id=kwargs.get('application_id'))
        
        # Check permissions
        is_owner = self.request.user == application.candidate
        is_employer = self.request.user == application.job.employer
        
        if not (is_owner or is_employer):
            context['error'] = 'You do not have permission to view this application.'
            return context
        
        context['application'] = application
        context['is_owner'] = is_owner
        context['is_employer'] = is_employer
        return context


class WithdrawApplicationView(LoginRequiredMixin, View):
    """Withdraw application."""
    
    def post(self, request, application_id):
        application = get_object_or_404(Application, id=application_id, candidate=request.user)
        if application.status == 'applied':
            application.delete()
            messages.success(request, 'Application withdrawn successfully.')
        else:
            messages.error(request, 'Cannot withdraw application that is already being reviewed.')
        return redirect('applications_views:my_applications')
