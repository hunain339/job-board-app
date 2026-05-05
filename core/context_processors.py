"""Context processors for templates."""


def theme_context(request):
    """Add theme and general context to all templates."""
    return {
        'site_name': 'JobBoard',
        'current_year': __import__('datetime').datetime.now().year,
        'user_is_candidate': request.user.is_authenticated and request.user.role == 'candidate',
        'user_is_employer': request.user.is_authenticated and request.user.role == 'employer',
        'user_is_admin': request.user.is_authenticated and request.user.role == 'admin',
    }
