"""Health check views."""

from django.http import JsonResponse


def health_check(request):
    """Return a minimal health response for liveness probes."""
    return JsonResponse({"status": "ok"})
