"""Job web view URLs."""

from django.urls import path
from . import views_web

app_name = 'jobs_views'

urlpatterns = [
    path('', views_web.JobListView.as_view(), name='job_list'),
    path('job/<slug:slug>/', views_web.JobDetailView.as_view(), name='job_detail'),
    path('post/', views_web.PostJobView.as_view(), name='post_job'),
    path('search/', views_web.JobSearchView.as_view(), name='job_search'),
]
