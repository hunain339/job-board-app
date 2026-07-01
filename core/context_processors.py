"""Context processors for templates."""


def theme_context(request):
    """Add theme and general context to all templates."""
    auth = request.user.is_authenticated
    return {
        'site_name': 'JobBoard',
        'current_year': __import__('datetime').datetime.now().year,
        'user_is_candidate': auth and request.user.role == 'candidate',
        'user_is_employer': auth and request.user.role == 'employer',
        'user_is_admin': auth and request.user.role == 'admin',
    }
