"""
URL configuration for job_board project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints
    path('api/users/', include('users.urls', namespace='api_users')),
    path('api/jobs/', include('jobs.urls', namespace='api_jobs')),
    path('api/applications/', include('applications.urls', namespace='api_applications')),
    
    # Web views
    path('', include('jobs.urls_views', namespace='jobs_views')),
    path('users/', include('users.urls_views', namespace='users_views')),
    path('applications/', include('applications.urls_views', namespace='applications_views')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
