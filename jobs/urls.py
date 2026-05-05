"""Job API URLs."""

from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import JobViewSet, JobCategoryViewSet

app_name = 'jobs'

router = SimpleRouter()
router.register(r'categories', JobCategoryViewSet, basename='category')
router.register(r'', JobViewSet, basename='job')

urlpatterns = [
    path('', include(router.urls)),
]
