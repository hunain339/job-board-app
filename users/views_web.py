"""Web views for users app."""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView, FormView
from django.core.cache import cache
from .forms import LoginForm, CandidateRegisterForm, EmployerRegisterForm

User = get_user_model()


class RegisterView(TemplateView):
    """Choose registration type."""
    template_name = 'auth/register.html'


class RegisterCandidateView(FormView):
    """Register as candidate."""
    template_name = 'auth/register_candidate.html'
    form_class = CandidateRegisterForm
    success_url = '/users/login/'
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Account created successfully. Please log in.')
        return super().form_valid(form)


class RegisterEmployerView(FormView):
    """Register as employer."""
    template_name = 'auth/register_employer.html'
    form_class = EmployerRegisterForm
    success_url = '/users/login/'
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Employer account created. Please log in.')
        return super().form_valid(form)


class LoginView(FormView):
    """User login."""
    template_name = 'auth/login.html'
    form_class = LoginForm
    success_url = '/users/dashboard/'

    def get_success_url(self):
        # Honour the ?next= redirect param if present
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url:
            return next_url
        return super().get_success_url()

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(self.request, email=email, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(
                    self.request,
                    'Your account is not active. Please verify your email or contact support.'
                )
                return self.form_invalid(form)
            login(self.request, user)
            messages.success(self.request, f'Welcome back, {user.first_name or user.email}!')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Invalid email or password.')
            return self.form_invalid(form)


class LogoutView(View):
    """User logout."""
    
    def post(self, request):
        logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('/')


class ProfileView(TemplateView):
    """User profile view."""
    template_name = 'auth/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User.objects.select_related('profile'), id=kwargs.get('user_id'))
        context['profile_user'] = user
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = '/users/login/'
    """User dashboard - role-specific."""
    
    def get_template_names(self):
        user = self.request.user
        if user.role == 'candidate':
            return ['auth/dashboard_candidate.html']
        elif user.role == 'employer':
            return ['auth/dashboard_employer.html']
        elif user.role == 'admin':
            return ['auth/dashboard_admin.html']
        return ['auth/dashboard.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        
        if user.role == 'candidate':
            from applications.models import Application
            from jobs.models import JobSavedByUser
            counts = cache.get_or_set(
                f'dashboard_candidate_counts_{user.id}',
                lambda: {
                    'applications_count': Application.objects.filter(candidate=user).count(),
                    'saved_jobs_count': JobSavedByUser.objects.filter(candidate=user).count(),
                },
                300,
            )
            context.update(counts)
            context['recent_applications'] = cache.get_or_set(
                f'dashboard_candidate_recent_{user.id}',
                lambda: list(
                    Application.objects.filter(candidate=user)
                    .select_related('job', 'job__employer', 'job__category')
                    .order_by('-created_at')[:5]
                ),
                300,
            )
        elif user.role == 'employer':
            from jobs.models import Job
            from applications.models import Application
            counts = cache.get_or_set(
                f'dashboard_employer_counts_{user.id}',
                lambda: {
                    'active_jobs_count': Job.objects.filter(employer=user, is_active=True).count(),
                    'total_applications_count': Application.objects.filter(job__employer=user).count(),
                },
                300,
            )
            context.update(counts)
            context['recent_applications'] = cache.get_or_set(
                f'dashboard_employer_recent_{user.id}',
                lambda: list(
                    Application.objects.filter(job__employer=user)
                    .select_related('job', 'job__category', 'candidate')
                    .order_by('-created_at')[:5]
                ),
                300,
            )
            
        return context
