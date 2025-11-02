"""
Authentication app URL configuration.
"""

from django.urls import path
from . import views

# No app_name to avoid namespace (tests expect 'signup', not 'authentication:signup')

urlpatterns = [
    # Index
    path('', views.index_view, name='index'),

    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Profile only (dashboard moved to analytics app)
    path('profile/', views.profile_view, name='profile'),
]