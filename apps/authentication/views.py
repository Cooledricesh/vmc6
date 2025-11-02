"""
Authentication views for user registration, login, and logout.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache

from .forms import SignupForm, LoginForm
from .models import User


def index_view(request):
    """
    Index page - shows login for anonymous, redirects authenticated users to dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    # Show login form for anonymous users
    form = LoginForm()
    return render(request, 'authentication/login.html', {
        'form': form,
        'title': '로그인'
    })


@never_cache
def signup_view(request):
    """
    User registration view.
    """
    # Redirect if already authenticated
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                '회원가입이 완료되었습니다. 관리자 승인 후 로그인하실 수 있습니다.'
            )
            return redirect('login')
    else:
        form = SignupForm()

    return render(request, 'authentication/signup.html', {
        'form': form,
        'title': '회원가입'
    })


@never_cache
def login_view(request):
    """
    User login view.
    """
    # Redirect if already authenticated
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)

            # Authenticate user (using email as username)
            user = authenticate(request, username=email, password=password)

            if user is not None and user.status == 'active':
                login(request, user)

                # Set session expiry based on remember_me
                if not remember_me:
                    request.session.set_expiry(0)  # Browser close
                else:
                    request.session.set_expiry(1209600)  # 2 weeks

                # Redirect to next page or dashboard
                next_page = request.GET.get('next', 'dashboard')
                return redirect(next_page)
            else:
                # Form validation should handle this, but just in case
                messages.error(request, '로그인에 실패했습니다.')
    else:
        form = LoginForm()

    return render(request, 'authentication/login.html', {
        'form': form,
        'title': '로그인'
    })


@login_required
def logout_view(request):
    """
    User logout view.
    """
    logout(request)
    messages.success(request, '로그아웃되었습니다.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """
    Dashboard view - main page after login.
    """
    # Get user's accessible departments
    user = request.user

    context = {
        'title': '대시보드',
        'user': user,
        'role': user.role,
        'department': user.department,
    }

    # Redirect to appropriate dashboard based on role
    if user.role == 'admin':
        return render(request, 'analytics/admin_dashboard.html', context)
    elif user.role == 'manager':
        return render(request, 'analytics/manager_dashboard.html', context)
    else:  # viewer
        return render(request, 'analytics/viewer_dashboard.html', context)


@login_required
def profile_view(request):
    """
    User profile view.
    """
    return render(request, 'authentication/profile.html', {
        'title': '내 정보',
        'user': request.user
    })
