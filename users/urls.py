"""User API URLs."""

from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import UserViewSet

app_name = 'users'

router = SimpleRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
