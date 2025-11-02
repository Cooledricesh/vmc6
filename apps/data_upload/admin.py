"""
Django Admin customization for data upload functionality.

Customizes admin interface for analytics models to support file uploads:
- DepartmentKPI: Upload KPI Excel/CSV files
- Publication: Upload publication data
- ResearchProject & ExecutionRecord: Upload research budget data
- Student: Upload student data

All uploads trigger parsers that validate and insert data into database.
"""
from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html

from apps.analytics.models import (
    DepartmentKPI,
    Publication,
    ResearchProject,
    ExecutionRecord,
    Student,
    UploadHistory,
)
from apps.data_upload.parsers import (
    DepartmentKPIParser,
    PublicationParser,
    ResearchBudgetParser,
    StudentParser,
)


@admin.register(DepartmentKPI)
class DepartmentKPIAdmin(admin.ModelAdmin):
    """Admin for Department KPI with file upload functionality."""

    list_display = ('evaluation_year', 'college', 'department', 'employment_rate', 'created_at')
    list_filter = ('evaluation_year', 'college')
    search_fields = ('college', 'department')
    ordering = ('-evaluation_year', 'college', 'department')
    readonly_fields = ('created_at',)

    change_list_template = 'admin/departmentkpi_changelist.html'

    def changelist_view(self, request, extra_context=None):
        """
        Override changelist view to handle file uploads.

        This allows admins to upload Excel/CSV files directly from the admin list page.
        """
        if request.method == 'POST' and request.FILES.get('kpi_file'):
            uploaded_file = request.FILES['kpi_file']

            # Save file temporarily
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                for chunk in uploaded_file.chunks():
                    tmp_file.write(chunk)
                tmp_filepath = tmp_file.name

            try:
                # Parse the file
                parser = DepartmentKPIParser()
                result = parser.parse(tmp_filepath, request.user)

                if result['success']:
                    messages.success(
                        request,
                        f"Successfully uploaded {result['rows_processed']} KPI records from {uploaded_file.name}"
                    )
                else:
                    messages.error(
                        request,
                        f"Failed to upload {uploaded_file.name}: {result['error_message']}"
                    )
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_filepath):
                    os.unlink(tmp_filepath)

        return super().changelist_view(request, extra_context)


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    """Admin for Publication with file upload functionality."""

    list_display = ('publication_id', 'title', 'first_author', 'journal_name', 'journal_grade', 'publication_date')
    list_filter = ('journal_grade', 'project_linked', 'publication_date')
    search_fields = ('publication_id', 'title', 'first_author', 'journal_name')
    ordering = ('-publication_date',)
    readonly_fields = ('created_at',)

    change_list_template = 'admin/publication_changelist.html'

    def changelist_view(self, request, extra_context=None):
        """Override changelist view to handle file uploads."""
        if request.method == 'POST' and request.FILES.get('publication_file'):
            uploaded_file = request.FILES['publication_file']

            import tempfile
            import os

            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                for chunk in uploaded_file.chunks():
                    tmp_file.write(chunk)
                tmp_filepath = tmp_file.name

            try:
                parser = PublicationParser()
                result = parser.parse(tmp_filepath, request.user)

                if result['success']:
                    messages.success(
                        request,
                        f"Successfully uploaded {result['rows_processed']} publication records from {uploaded_file.name}"
                    )
                else:
                    messages.error(
                        request,
                        f"Failed to upload {uploaded_file.name}: {result['error_message']}"
                    )
            finally:
                if os.path.exists(tmp_filepath):
                    os.unlink(tmp_filepath)

        return super().changelist_view(request, extra_context)


@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    """Admin for Research Projects."""

    list_display = ('project_number', 'project_name', 'principal_investigator', 'department', 'total_budget', 'created_at')
    list_filter = ('department', 'funding_agency')
    search_fields = ('project_number', 'project_name', 'principal_investigator')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ExecutionRecord)
class ExecutionRecordAdmin(admin.ModelAdmin):
    """Admin for Execution Records with file upload functionality."""

    list_display = ('execution_id', 'project', 'execution_date', 'expense_category', 'amount', 'status')
    list_filter = ('status', 'execution_date')
    search_fields = ('execution_id', 'project__project_number', 'project__project_name')
    ordering = ('-execution_date',)
    readonly_fields = ('created_at',)

    change_list_template = 'admin/executionrecord_changelist.html'

    def changelist_view(self, request, extra_context=None):
        """Override changelist view to handle research budget file uploads."""
        if request.method == 'POST' and request.FILES.get('budget_file'):
            uploaded_file = request.FILES['budget_file']

            import tempfile
            import os

            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                for chunk in uploaded_file.chunks():
                    tmp_file.write(chunk)
                tmp_filepath = tmp_file.name

            try:
                parser = ResearchBudgetParser()
                result = parser.parse(tmp_filepath, request.user)

                if result['success']:
                    messages.success(
                        request,
                        f"Successfully uploaded {result['rows_processed']} execution records from {uploaded_file.name}"
                    )
                else:
                    messages.error(
                        request,
                        f"Failed to upload {uploaded_file.name}: {result['error_message']}"
                    )
            finally:
                if os.path.exists(tmp_filepath):
                    os.unlink(tmp_filepath)

        return super().changelist_view(request, extra_context)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin for Student with file upload functionality."""

    list_display = ('student_number', 'name', 'department', 'grade', 'program_type', 'enrollment_status', 'admission_year')
    list_filter = ('enrollment_status', 'program_type', 'grade', 'admission_year')
    search_fields = ('student_number', 'name', 'department')
    ordering = ('-admission_year', 'student_number')
    readonly_fields = ('created_at', 'updated_at')

    change_list_template = 'admin/student_changelist.html'

    def changelist_view(self, request, extra_context=None):
        """Override changelist view to handle file uploads."""
        if request.method == 'POST' and request.FILES.get('student_file'):
            uploaded_file = request.FILES['student_file']

            import tempfile
            import os

            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                for chunk in uploaded_file.chunks():
                    tmp_file.write(chunk)
                tmp_filepath = tmp_file.name

            try:
                parser = StudentParser()
                result = parser.parse(tmp_filepath, request.user)

                if result['success']:
                    messages.success(
                        request,
                        f"Successfully uploaded {result['rows_processed']} student records from {uploaded_file.name}"
                    )
                else:
                    messages.error(
                        request,
                        f"Failed to upload {uploaded_file.name}: {result['error_message']}"
                    )
            finally:
                if os.path.exists(tmp_filepath):
                    os.unlink(tmp_filepath)

        return super().changelist_view(request, extra_context)


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
