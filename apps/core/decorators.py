"""
Authentication and permission decorators for the application.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def role_required(allowed_roles):
    """
    Decorator to check if user has one of the allowed roles.

    Usage:
        @role_required(['admin', 'manager'])
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if hasattr(request.user, 'role') and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, '권한이 없습니다.')
                return redirect('dashboard')
        return wrapper
    return decorator


def active_user_required(view_func):
    """
    Decorator to check if user is active (not pending or inactive).

    Usage:
        @active_user_required
        def my_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'is_active') and request.user.is_active == 'active':
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, '활성화된 사용자만 접근 가능합니다.')
            return redirect('login')
    return wrapper


def admin_required(view_func):
    """
    Decorator to check if user is an admin.
    Shorthand for @role_required(['admin'])

    Usage:
        @admin_required
        def my_view(request):
            ...
    """
    return role_required(['admin'])(view_func)


def manager_required(view_func):
    """
    Decorator to check if user is a manager or admin.
    Shorthand for @role_required(['admin', 'manager'])

    Usage:
        @manager_required
        def my_view(request):
            ...
    """
    return role_required(['admin', 'manager'])(view_func)