"""
Django Admin customization for data management.

Clean admin interface for viewing and managing data records.
File uploads should be done via the dedicated upload page: /data/upload/
"""
from django.contrib import admin

from apps.analytics.models import (
    DepartmentKPI,
    Publication,
    ResearchProject,
    ExecutionRecord,
    Student,
    UploadHistory,
)


@admin.register(DepartmentKPI)
class DepartmentKPIAdmin(admin.ModelAdmin):
    """Admin for Department KPI - data viewing and management only."""

    list_display = ('evaluation_year', 'college', 'department', 'employment_rate', 'created_at')
    list_filter = ('evaluation_year', 'college')
    search_fields = ('college', 'department')
    ordering = ('-evaluation_year', 'college', 'department')
    readonly_fields = ('created_at',)

    def has_add_permission(self, request):
        """Only admin can add data."""
        return request.user.role == 'admin'

    def has_change_permission(self, request, obj=None):
        """Only admin can edit data."""
        return request.user.role == 'admin'

    def has_delete_permission(self, request, obj=None):
        """Only admin can delete data."""
        return request.user.role == 'admin'


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    """Admin for Publication - data viewing and management only."""

    list_display = ('publication_id', 'title', 'first_author', 'journal_name', 'journal_grade', 'publication_date')
    list_filter = ('journal_grade', 'project_linked', 'publication_date')
    search_fields = ('publication_id', 'title', 'first_author', 'journal_name')
    ordering = ('-publication_date',)
    readonly_fields = ('created_at',)

    def has_add_permission(self, request):
        """Only admin can add data."""
        return request.user.role == 'admin'

    def has_change_permission(self, request, obj=None):
        """Only admin can edit data."""
        return request.user.role == 'admin'

    def has_delete_permission(self, request, obj=None):
        """Only admin can delete data."""
        return request.user.role == 'admin'


@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    """Admin for Research Projects - data viewing and management only."""

    list_display = ('project_number', 'project_name', 'principal_investigator', 'department', 'total_budget', 'created_at')
    list_filter = ('department', 'funding_agency')
    search_fields = ('project_number', 'project_name', 'principal_investigator')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    def has_add_permission(self, request):
        """Only admin can add data."""
        return request.user.role == 'admin'

    def has_change_permission(self, request, obj=None):
        """Only admin can edit data."""
        return request.user.role == 'admin'

    def has_delete_permission(self, request, obj=None):
        """Only admin can delete data."""
        return request.user.role == 'admin'


@admin.register(ExecutionRecord)
class ExecutionRecordAdmin(admin.ModelAdmin):
    """Admin for Execution Records - data viewing and management only."""

    list_display = ('execution_id', 'project', 'execution_date', 'expense_category', 'amount', 'status')
    list_filter = ('status', 'execution_date')
    search_fields = ('execution_id', 'project__project_number', 'project__project_name')
    ordering = ('-execution_date',)
    readonly_fields = ('created_at',)

    def has_add_permission(self, request):
        """Only admin can add data."""
        return request.user.role == 'admin'

    def has_change_permission(self, request, obj=None):
        """Only admin can edit data."""
        return request.user.role == 'admin'

    def has_delete_permission(self, request, obj=None):
        """Only admin can delete data."""
        return request.user.role == 'admin'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin for Student - data viewing and management only."""

    list_display = ('student_number', 'name', 'department', 'grade', 'program_type', 'enrollment_status', 'admission_year')
    list_filter = ('enrollment_status', 'program_type', 'grade', 'admission_year')
    search_fields = ('student_number', 'name', 'department')
    ordering = ('-admission_year', 'student_number')
    readonly_fields = ('created_at', 'updated_at')

    def has_add_permission(self, request):
        """Only admin can add data."""
        return request.user.role == 'admin'

    def has_change_permission(self, request, obj=None):
        """Only admin can edit data."""
        return request.user.role == 'admin'

    def has_delete_permission(self, request, obj=None):
        """Only admin can delete data."""
        return request.user.role == 'admin'


@admin.register(UploadHistory)
class UploadHistoryAdmin(admin.ModelAdmin):
    """Admin for Upload History - Read-only audit log."""

    list_display = ('file_name', 'data_type', 'user', 'upload_date', 'status', 'rows_processed')
    list_filter = ('data_type', 'status', 'upload_date')
    search_fields = ('file_name', 'user__email', 'user__username')
    ordering = ('-upload_date',)
    readonly_fields = ('user', 'file_name', 'file_size', 'data_type', 'upload_date', 'status', 'rows_processed', 'error_message')

    def has_add_permission(self, request):
        """Disable adding upload history manually."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing upload history."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deleting upload history (for cleanup)."""
        return request.user.is_superuser
