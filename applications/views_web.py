"""Web views for applications app."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, ListView

from django.db.models import Q
from jobs.models import Job

from django.http import HttpResponse, Http404
from .models import Application
from .services import update_application_status


class MyApplicationsView(LoginRequiredMixin, ListView):
    """View candidate's applications."""

    login_url = '/users/login/'
    template_name = 'applications/my_applications.html'
    context_object_name = 'applications'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.role != 'candidate':
            return Application.objects.none()

        return (
            Application.objects.filter(candidate=self.request.user)
            .select_related('job', 'job__employer', 'job__category')
            .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role != 'candidate':
            context['error'] = 'Only candidates can view applications.'
        return context


class JobApplicationsView(LoginRequiredMixin, ListView):
    """View applications for a job (employer only)."""

    login_url = '/users/login/'
    template_name = 'applications/job_applications.html'
    context_object_name = 'applications'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        self.job = get_object_or_404(
            Job.objects.select_related('employer', 'category'),
            id=kwargs.get('job_id'),
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.role != 'employer':
            return Application.objects.none()
        if self.job.employer != self.request.user:
            return Application.objects.none()

        queryset = (
            Application.objects.filter(job=self.job)
            .select_related('candidate', 'job', 'job__employer', 'job__category')
            .order_by('-created_at')
        )

        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.prefetch_related(
            'employer_notes__employer',
            'status_history__changed_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = self.job
        if self.request.user.role != 'employer':
            context['error'] = 'Only employers can view applications.'
            return context
        if self.job.employer != self.request.user:
            context['error'] = 'You do not have permission to view these applications.'
            return context

        counts_cache_key = f'job_application_counts_{self.job.id}'
        counts = cache.get_or_set(
            counts_cache_key,
            lambda: {
                'total_applications': (
                    Application.objects.filter(job=self.job)
                ).count(),
                'applied_count': (
                    Application.objects.filter(job=self.job, status='applied')
                ).count(),
                'reviewing_count': (
                    Application.objects.filter(job=self.job, status='reviewing')
                ).count(),
                'interview_count': (
                    Application.objects.filter(job=self.job, status='interview')
                ).count(),
                'hired_count': (
                    Application.objects.filter(job=self.job, status='hired')
                ).count(),
            },
            300,
        )
        context.update(counts)
        context['status_choices'] = Application.STATUS_CHOICES
        return context


class ApplicationDetailView(LoginRequiredMixin, DetailView):
    """View application detail."""

    login_url = '/users/login/'
    template_name = 'applications/application_detail.html'
    context_object_name = 'application'
    pk_url_kwarg = 'application_id'

    def get_queryset(self):
        user = self.request.user
        qs = (
            Application.objects.select_related(
                'candidate',
                'job',
                'job__employer',
                'job__category') .prefetch_related(
                'employer_notes__employer',
                'status_history__changed_by'))
        if user.role == 'admin':
            return qs
        return qs.filter(Q(candidate=user) | Q(job__employer=user))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.object

        context['is_owner'] = self.request.user == application.candidate
        context['is_employer'] = self.request.user == application.job.employer
        return context


class WithdrawApplicationView(LoginRequiredMixin, View):
    """Withdraw application."""

    login_url = '/users/login/'

    def post(self, request, application_id):
        try:
            application = Application.objects.get(
                id=application_id, candidate=request.user)
            if application.status == 'applied':
                application.delete()
                messages.success(request, 'Application withdrawn successfully.')
            else:
                msg = 'Cannot withdraw application that is already being reviewed.'
                messages.error(request, msg)
        except Application.DoesNotExist:
            pass  # Already withdrawn or does not exist
        return redirect('applications_views:my_applications')


class UpdateApplicationStatusView(LoginRequiredMixin, View):
    """Update application status (employer only)."""

    login_url = '/users/login/'

    def post(self, request, application_id):
        application = get_object_or_404(
            Application,
            id=application_id,
            job__employer=request.user)
        new_status = request.POST.get('status')
        if new_status in dict(Application.STATUS_CHOICES):
            update_application_status(
                application=application,
                changed_by=request.user,
                status=new_status
            )
            messages.success(request, f'Application status updated to {new_status}.')
        return redirect(
            'applications_views:job_applications',
            job_id=application.job.id)


class UpdateApplicationRatingView(LoginRequiredMixin, View):
    """Update application rating (employer only)."""

    login_url = '/users/login/'

    def post(self, request, application_id):
        application = get_object_or_404(
            Application,
            id=application_id,
            job__employer=request.user)
        try:
            rating = int(request.POST.get('rating', 0))
            if 0 <= rating <= 5:
                application.rating = rating
                application.save(update_fields=['rating'])
                messages.success(request, 'Rating updated.')
        except ValueError:
            pass
        return redirect(
            'applications_views:job_applications',
            job_id=application.job.id)


class ViewResumeView(LoginRequiredMixin, View):
    """View application resume."""

    login_url = '/users/login/'

    def get(self, request, application_id):
        user = request.user
        qs = Application.objects.all()
        if user.role != 'admin':
            qs = qs.filter(Q(candidate=user) | Q(job__employer=user))

        application = get_object_or_404(qs, id=application_id)
        if not application.resume:
            raise Http404("Resume not found")

        response = HttpResponse(
            application.resume.read(),
            content_type='application/pdf',
        )
        filename = application.resume.name.split('/')[-1]
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
