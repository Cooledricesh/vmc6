"""
Data Upload Views

Provides unified smart file upload interface
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os


@login_required(login_url='/login/')
def upload_csv_view(request):
    """
    Unified smart file upload view.

    Automatically identifies file type by headers and routes to appropriate parser.

    Permission: Admin only
    """
    # Check if user is admin
    if request.user.role != 'admin':
        messages.error(request, '데이터 업로드는 관리자만 가능합니다.')
        return redirect('dashboard')

    if request.method == 'POST':
        uploaded_file = request.FILES.get('csv_file')

        if not uploaded_file:
            messages.error(request, '파일이 선택되지 않았습니다.')
            return redirect('data_upload:upload_csv')

        # Save file temporarily
        file_name = uploaded_file.name
        temp_path = default_storage.save(f'temp/{file_name}', ContentFile(uploaded_file.read()))
        temp_full_path = os.path.join(default_storage.location, temp_path)

        try:
            # Import here to avoid circular dependency
            from apps.data_upload.utils import identify_file_type

            # Identify file type
            ParserClass = identify_file_type(temp_full_path)

            if ParserClass is None:
                messages.error(request, '파일의 종류를 인식할 수 없습니다. 파일 헤더를 확인해주세요.')
                default_storage.delete(temp_path)
                return redirect('data_upload:upload_csv')

            # Parse file using identified parser
            parser = ParserClass()
            result = parser.parse(temp_full_path, request.user)

            if result['success']:
                messages.success(
                    request,
                    f"{result['rows_processed']}개의 데이터가 성공적으로 처리되었습니다."
                )
                # Redirect to appropriate analytics page based on data type
                return redirect('dashboard')
            else:
                messages.error(request, f"파일 처리 중 오류 발생: {result['error_message']}")

        except Exception as e:
            messages.error(request, f"예상치 못한 오류 발생: {str(e)}")

        finally:
            # Clean up temporary file
            if default_storage.exists(temp_path):
                default_storage.delete(temp_path)

        return redirect('data_upload:upload_csv')

    # GET request - show upload form
    return render(request, 'data_upload/upload_form.html', {
        'title': 'CSV 데이터 통합 업로드'
    })
