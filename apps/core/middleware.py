"""
Session validation middleware for the application.
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout


class SessionValidationMiddleware:
    """
    Middleware to validate user sessions and handle inactive users.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Public paths that don't require authentication
        self.public_paths = [
            reverse('login'),
            reverse('signup'),
            reverse('index'),
            '/static/',
            '/media/',
            '/admin/',
        ]

    def __call__(self, request):
        # Check if the path is public
        is_public = any(
            request.path.startswith(path) for path in self.public_paths
        )

        # If not public and user is not authenticated, redirect to login
        if not is_public and not request.user.is_authenticated:
            # Get the current path for the next parameter
            next_url = request.path
            if request.GET:
                next_url += '?' + request.GET.urlencode()

            # Don't add trailing slash to the next parameter
            next_url = next_url.rstrip('/')

            return redirect(f"{reverse('login')}?next={next_url}")

        # If user is authenticated but inactive, log them out
        if (request.user.is_authenticated and
            hasattr(request.user, 'is_active') and
            not request.user.is_active):
            logout(request)
            return redirect('login')

        response = self.get_response(request)
        return response