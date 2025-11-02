"""
Data filtering functions for analytics.

This module contains functions to filter Django querysets based on various criteria:
- Date ranges
- Department access
- College access
- User permissions (role-based)
- Multiple combined filters

These filters are designed to work with permission-based data access control
where admins/managers see all data, but viewers only see their own department.
"""

from typing import List, Optional, Dict, Any
from datetime import date
from django.db.models import QuerySet
from django.contrib.auth import get_user_model

User = get_user_model()


def filter_by_date_range(
    queryset: QuerySet,
    date_field: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> QuerySet:
    """
    Filter queryset by date range.

    Args:
        queryset: Django queryset to filter
        date_field: Name of the date field to filter on
        start_date: Optional start date (inclusive)
        end_date: Optional end date (inclusive)

    Returns:
        Filtered queryset

    Example:
        >>> kpis = DepartmentKPI.objects.all()
        >>> filtered = filter_by_date_range(
        ...     kpis,
        ...     'base_date',
        ...     start_date=date(2022, 1, 1),
        ...     end_date=date(2022, 12, 31)
        ... )
    """
    if start_date is not None:
        queryset = queryset.filter(**{f'{date_field}__gte': start_date})

    if end_date is not None:
        queryset = queryset.filter(**{f'{date_field}__lte': end_date})

    return queryset


def filter_by_department(
    queryset: QuerySet,
    departments: Optional[List[str]] = None
) -> QuerySet:
    """
    Filter queryset by department names.

    Args:
        queryset: Django queryset to filter
        departments: List of department names to include (None = all departments)

    Returns:
        Filtered queryset

    Example:
        >>> kpis = DepartmentKPI.objects.all()
        >>> filtered = filter_by_department(
        ...     kpis,
        ...     ['컴퓨터공학과', '전자공학과']
        ... )
    """
    if departments is not None and len(departments) > 0:
        queryset = queryset.filter(department__in=departments)

    return queryset


def filter_by_college(
    queryset: QuerySet,
    colleges: Optional[List[str]] = None
) -> QuerySet:
    """
    Filter queryset by college names.

    Args:
        queryset: Django queryset to filter
        colleges: List of college names to include (None = all colleges)

    Returns:
        Filtered queryset

    Example:
        >>> kpis = DepartmentKPI.objects.all()
        >>> filtered = filter_by_college(
        ...     kpis,
        ...     ['공과대학', '자연과학대학']
        ... )
    """
    if colleges is not None and len(colleges) > 0:
        queryset = queryset.filter(college__in=colleges)

    return queryset


def apply_user_permission_filter(
    queryset: QuerySet,
    user: User
) -> QuerySet:
    """
    Apply permission-based filtering based on user role.

    Permission rules:
    - admin: See all data
    - manager: See all data
    - viewer: See only own department's data

    Args:
        queryset: Django queryset to filter
        user: User object with role and department

    Returns:
        Filtered queryset based on user permissions

    Example:
        >>> kpis = DepartmentKPI.objects.all()
        >>> filtered = apply_user_permission_filter(kpis, request.user)
    """
    # Admin and manager can see all data
    if user.role in ['admin', 'manager']:
        return queryset

    # Viewer can only see their own department
    if user.role == 'viewer':
        return queryset.filter(department=user.department)

    # Default: no access
    return queryset.none()


def apply_multiple_filters(
    queryset: QuerySet,
    filters: Dict[str, Any],
    date_field: str = 'created_at'
) -> QuerySet:
    """
    Apply multiple filters to a queryset.

    This is a convenience function that applies all relevant filters
    based on the provided filter dictionary.

    Supported filter keys:
    - 'start_date': Start date for date range
    - 'end_date': End date for date range
    - 'departments': List of department names
    - 'colleges': List of college names
    - 'user': User object for permission filtering

    Args:
        queryset: Django queryset to filter
        filters: Dictionary of filter parameters
        date_field: Name of the date field (default: 'created_at')

    Returns:
        Filtered queryset with all applicable filters applied

    Example:
        >>> kpis = DepartmentKPI.objects.all()
        >>> filters = {
        ...     'start_date': date(2022, 1, 1),
        ...     'end_date': date(2022, 12, 31),
        ...     'departments': ['컴퓨터공학과'],
        ...     'user': request.user
        ... }
        >>> filtered = apply_multiple_filters(kpis, filters, 'base_date')
    """
    # Apply date range filter
    if 'start_date' in filters or 'end_date' in filters:
        queryset = filter_by_date_range(
            queryset,
            date_field,
            start_date=filters.get('start_date'),
            end_date=filters.get('end_date')
        )

    # Apply department filter
    if 'departments' in filters:
        queryset = filter_by_department(queryset, filters.get('departments'))

    # Apply college filter
    if 'colleges' in filters:
        queryset = filter_by_college(queryset, filters.get('colleges'))

    # Apply user permission filter
    if 'user' in filters:
        queryset = apply_user_permission_filter(queryset, filters.get('user'))

    return queryset
