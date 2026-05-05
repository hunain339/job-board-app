"""Application web view URLs."""

from django.urls import path
from . import views_web

app_name = 'applications_views'

urlpatterns = [
    path('my-applications/', views_web.MyApplicationsView.as_view(), name='my_applications'),
    path('job/<uuid:job_id>/applications/', views_web.JobApplicationsView.as_view(), name='job_applications'),
    path('<uuid:application_id>/', views_web.ApplicationDetailView.as_view(), name='application_detail'),
    path('<uuid:application_id>/withdraw/', views_web.WithdrawApplicationView.as_view(), name='withdraw_application'),
]
