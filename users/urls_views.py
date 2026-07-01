"""User web view URLs."""

from django.urls import path
from . import views_web

app_name = 'users_views'

urlpatterns = [
    path(
        'register/',
        views_web.RegisterView.as_view(),
        name='register'),
    path(
        'register/candidate/',
        views_web.RegisterCandidateView.as_view(),
        name='register_candidate'),
    path(
        'register/employer/',
        views_web.RegisterEmployerView.as_view(),
        name='register_employer'),
    path(
        'login/',
        views_web.LoginView.as_view(),
        name='login'),
    path(
        'logout/',
        views_web.LogoutView.as_view(),
        name='logout'),
    path(
        'profile/<uuid:user_id>/',
        views_web.ProfileView.as_view(),
        name='profile'),
    path(
        'dashboard/',
        views_web.DashboardView.as_view(),
        name='dashboard'),
]
