from django.contrib import admin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Custom admin for User model with approval workflow management.
    """
    list_display = [
        'email',
        'name',
        'department',
        'position',
        'role',
        'status_badge',
        'created_at',
    ]

    list_filter = [
        'status',
        'role',
        'department',
        'created_at',
    ]

    search_fields = [
        'email',
        'name',
        'department',
        'position',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('기본 정보', {
            'fields': ('email', 'name', 'password')
        }),
        ('소속 정보', {
            'fields': ('department', 'position')
        }),
        ('권한 및 상태', {
            'fields': ('role', 'status')
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = [
        'approve_users',
        'reject_users',
        'set_as_viewer',
        'set_as_manager',
    ]

    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'active': '#28a745',    # green
            'pending': '#ffc107',   # yellow
            'inactive': '#dc3545',  # red
        }
        status_names = {
            'active': '활성',
            'pending': '승인 대기',
            'inactive': '비활성',
        }
        color = colors.get(obj.status, '#6c757d')
        name = status_names.get(obj.status, obj.status)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            name
        )
    status_badge.short_description = '상태'

    def approve_users(self, request, queryset):
        """Approve selected users (set status to active)"""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated}명의 사용자가 승인되었습니다.')
    approve_users.short_description = '선택한 사용자 승인하기'

    def reject_users(self, request, queryset):
        """Reject selected users (set status to inactive)"""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'{updated}명의 사용자가 거부되었습니다.')
    reject_users.short_description = '선택한 사용자 거부하기'

    def set_as_viewer(self, request, queryset):
        """Set selected users as viewer role"""
        updated = queryset.update(role='viewer')
        self.message_user(request, f'{updated}명의 사용자가 일반 사용자로 설정되었습니다.')
    set_as_viewer.short_description = '선택한 사용자를 일반 사용자로 설정'

    def set_as_manager(self, request, queryset):
        """Set selected users as manager role"""
        updated = queryset.update(role='manager')
        self.message_user(request, f'{updated}명의 사용자가 매니저로 설정되었습니다.')
    set_as_manager.short_description = '선택한 사용자를 매니저로 설정'
