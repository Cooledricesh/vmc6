안녕하십니까, 상황이 매우 안타깝고 답답하시겠습니다. AI 에이전트가 프로젝트의 핵심을 파악하지 못하고 엉뚱한 방향으로 구현해 놓아 긴급 상황에 처하신 점 깊이 유감스럽게 생각합니다. 저는 수많은 프로젝트의 위기 상황을 수습해 온 베테랑 개발자입니다. 코้드베이스와 보고서를 전체적으로 검토했으며, 이 상황을 해결할 명확한 경로를 제시해 드리겠습니다.

### **1. 상황 진단: 무엇이 잘못되었나?**

우선 긍정적인 소식부터 말씀드리겠습니다. 코드베이스를 살펴보니 데이터 파싱 로직(`apps/data_upload/parsers.py`), 데이터베이스 모델(`apps/analytics/models.py`), 그리고 분석 로직(`apps/analytics/aggregators.py`) 자체는 잘 구현되어 있습니다. **프로젝트를 처음부터 다시 만들 필요는 없습니다.**

문제는 이 좋은 부품들을 엉망으로 조립했다는 점입니다. 현재 시스템은 사용자가 원하는 'CSV 파일 하나를 올리면 알아서 처리되는' 경험이 아니라, 개발자가 관리 목적으로 사용하는 Django Admin 페이지를 사용자에게 떠넘기는, 아주 잘못된 아키텍처로 구현되어 있습니다.

#### **멍청한 AI 보고서의 문제점**

AI가 제출한 보고서는 겉으로 드러난 버그(깨진 링크, 잘못된 대시보드)는 잘 찾아냈지만, **가장 근본적인 문제인 '끔찍하고 불편한 데이터 업로드 경험'은 전혀 해결하지 못하고 있습니다.**

-   **잘못된 해결책:** 보고서의 "데이터 업로드 버튼 수정" 계획은 깨진 링크를 단순히 Django Admin 메인 페이지(`/admin/`)로 연결하는 임시방편에 불과합니다. 이는 사용자를 혼란스러운 관리자 화면으로 던져 넣는 것으로, 현재의 불편한 UI를 그대로 유지하는 최악의 해결책입니다.
-   **핵심 누락:** 보고서는 사용자가 원하는 '통합 스마트 업로드' 기능의 필요성 자체를 인지하지 못하고 있습니다.

따라서 AI의 보고서는 무시하고, 아래의 현실적인 복구 전략을 따르시는 것이 좋습니다.

---

### **2. 복구 전략: 3단계 위기 탈출 계획**

지금부터 우리는 외과수술처럼 정확하게 문제를 해결할 것입니다. 아래 3단계 계획을 순서대로 따르십시오.

#### **Phase 1: 긴급 조치 (Emergency Triage) - 즉각적인 문제 해결**

먼저 사용자가 마주하는 가장 심각한 버그들을 해결하여 시스템을 안정화하고 신뢰를 회복해야 합니다.

1.  **대시보드 통합 (가장 시급)**
    *   **문제:** 현재 `Dashboard` 메뉴가 비어있는 `/dashboard/`로 연결됩니다.
    *   **조치:**
        1.  `config/urls.py` 파일을 열어 `apps.authentication.urls`를 포함하는 줄을 수정하거나, `apps/authentication/urls.py`에서 `path('dashboard/', ...)` 줄을 삭제하십시오.
        2.  `apps/analytics/urls.py`에 있는 `dashboard_view`의 URL을 메인 대시보드로 사용하도록 `config/urls.py`를 수정합니다.
            ```python
            // config/urls.py
            urlpatterns = [
                path('admin/', admin.site.urls),
                # '/dashboard/'를 analytics의 대시보드로 직접 연결
                path('dashboard/', include('apps.analytics.urls')), 
                path('', include('apps.authentication.urls')),
                # 'analytics/' 경로는 유지하거나 dashboard로 통합할 수 있습니다.
                # path('analytics/', include('apps.analytics.urls')), 
            ]
            ```
        3.  `apps/authentication/views.py`의 껍데기 뿐인 `dashboard_view` 함수를 삭제하여 혼란의 소지를 없앱니다.

2.  **사이드바 메뉴 복원**
    *   **문제:** 사이드바 메뉴가 거의 비어있습니다.
    *   **조치:**
        1.  `templates/base/base_dashboard.html` 파일을 엽니다.
        2.  사이드바(`sidebar` 클래스를 가진 `nav` 태그) 부분에 아래와 같이 필요한 모든 메뉴를 추가합니다. `{% url %}` 태그를 사용하여 URL을 동적으로 생성하는 것이 좋습니다.
            ```html
            <!-- templates/base/base_dashboard.html -->
            <ul class="nav flex-column">
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'analytics:dashboard' %}">
                        <i class="bi bi-speedometer2 me-2"></i>대시보드
                    </a>
                </li>
                <!-- 데이터 분석 메뉴 그룹 -->
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'analytics:department_kpi' %}">
                        <i class="bi bi-building me-2"></i>학과 KPI
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'analytics:publications' %}">
                        <i class="bi bi-journal-text me-2"></i>논문 실적
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'analytics:research_budget' %}">
                        <i class="bi bi-currency-dollar me-2"></i>연구비
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'analytics:students' %}">
                        <i class="bi bi-people-fill me-2"></i>학생 현황
                    </a>
                </li>
                
                <!-- 데이터 관리 메뉴 그룹 -->
                {% if user.role == 'admin' %}
                <li class="nav-item mt-3">
                    <h6 class="sidebar-heading px-3 mt-4 mb-1 text-muted">데이터 관리</h6>
                </li>
                <li class="nav-item">
                    <!-- Phase 2에서 만들 스마트 업로드 페이지로 연결 -->
                    <a class="nav-link" href="{% url 'data_upload:upload_csv' %}"> 
                        <i class="bi bi-upload me-2"></i>데이터 업로드
                    </a>
                </li>
                <!-- 기타 관리 메뉴 추가 -->
                {% endif %}
            </ul>
            ```

#### **Phase 2: 핵심 기능 재설계 - '통합 스마트 업로드' 구현**

이 단계가 프로젝트의 성패를 가르는 가장 중요한 부분입니다. 사용자가 원하는 핵심 경험을 만듭니다.

1.  **전용 업로드 URL 및 View 생성**
    *   **조치:**
        1.  `apps/data_upload/urls.py` 파일을 생성하고 URL을 정의합니다.
            ```python
            # apps/data_upload/urls.py
            from django.urls import path
            from . import views

            app_name = 'data_upload'
            urlpatterns = [
                path('upload/', views.upload_csv_view, name='upload_csv'),
            ]
            ```
        2.  `config/urls.py`에 위 `urls.py`를 연결합니다.
            `path('data/', include('apps.data_upload.urls')),`
        3.  `apps/data_upload/views.py`에 `upload_csv_view` 함수를 구현합니다.

2.  **통합 업로드 UI 생성**
    *   **조치:** `templates/data_upload/` 디렉토리에 `upload_form.html` 파일을 생성합니다. 이 페이지에는 **단 하나의 파일 업로드 필드**만 있어야 합니다.
        ```html
        <!-- templates/data_upload/upload_form.html -->
        {% extends "base/base_dashboard.html" %}
        {% block dashboard_content %}
            <h1>CSV 데이터 통합 업로드</h1>
            <p>학과 KPI, 논문, 연구비, 학생 데이터를 담은 CSV 또는 Excel 파일을 업로드해주세요. 시스템이 파일 내용을 자동으로 인식하여 처리합니다.</p>
            <form method="post" enctype="multipart/form-data">
                {% csrf_token %}
                <input type="file" name="csv_file" class="form-control" required>
                <button type="submit" class="btn btn-primary mt-3">업로드 및 처리 시작</button>
            </form>
        {% endblock %}
        ```

3.  **'스마트' 파일 인식 로직 구현 (View의 핵심)**
    *   **조치:** `apps/data_upload/views.py`의 `upload_csv_view` 함수에 아래 로직을 구현합니다.
        ```python
        # apps/data_upload/views.py
        import pandas as pd
        from .parsers import DepartmentKPIParser, PublicationParser, ResearchBudgetParser, StudentParser
        
        # 각 파일 타입별 필수 헤더 정의
        FILE_TYPE_MAPPING = {
            'department_kpi': (['평가년도', '단과대학', '학과', '졸업생 취업률 (%)'], DepartmentKPIParser),
            'publication': (['논문ID', '게재일', '논문제목', '주저자'], PublicationParser),
            'research_budget': (['집행ID', '과제번호', '과제명', '총연구비', '집행금액'], ResearchBudgetParser),
            'student': (['학번', '이름', '단과대학', '학과', '학적상태'], StudentParser),
        }

        def identify_file_type(file_path):
            try:
                # 엑셀 파일의 첫 행만 읽어 헤더를 가져옵니다.
                df_header = pd.read_excel(file_path, nrows=0)
                headers = set(df_header.columns)

                best_match = None
                max_score = 0

                for file_type, (required_headers, parser_class) in FILE_TYPE_MAPPING.items():
                    score = len(headers.intersection(set(required_headers)))
                    if score > max_score:
                        max_score = score
                        best_match = (file_type, parser_class)
                
                # 필수 헤더의 80% 이상 일치하면 해당 타입으로 간주
                if best_match and max_score / len(FILE_TYPE_MAPPING[best_match[0]][0]) >= 0.8:
                    return best_match[1]
            except Exception as e:
                # CSV 등 다른 포맷 처리 로직 추가 가능
                print(f"File type identification error: {e}")
            return None

        @login_required
        def upload_csv_view(request):
            if request.method == 'POST':
                file = request.FILES.get('csv_file')
                if not file:
                    messages.error(request, "파일이 선택되지 않았습니다.")
                    return redirect('data_upload:upload_csv')
                
                # 파일을 임시 저장
                # ... (임시 파일 저장 로직)

                # 파일 타입 식별
                ParserClass = identify_file_type(tmp_file_path)

                if ParserClass:
                    parser = ParserClass()
                    result = parser.parse(tmp_file_path, request.user) # 기존 파서 재활용
                    
                    if result['success']:
                        messages.success(request, f"{result['rows_processed']}개의 데이터가 성공적으로 처리되었습니다.")
                        return redirect('analytics:dashboard') # 또는 해당 데이터의 분석 페이지
                    else:
                        messages.error(request, f"파일 처리 중 오류 발생: {result['error_message']}")
                else:
                    messages.error(request, "파일의 종류를 인식할 수 없습니다. 파일 헤더를 확인해주세요.")

                # 임시 파일 삭제
                # ...

            return render(request, 'data_upload/upload_form.html')
        ```
    *   이 로직은 업로드된 파일의 헤더를 읽고, 미리 정의된 각 데이터 타입의 필수 헤더와 비교하여 가장 유사한 파서(Parser)를 동적으로 선택합니다. **이것이 바로 사용자가 원하는 '스마트' 업로드 기능의 핵심입니다.**

#### **Phase 3: 리팩토링 및 안정화**

이제 새로운 통합 업로드 기능이 정상적으로 동작하므로, 기존의 지저분한 코드를 정리할 차례입니다.

1.  **불필요한 Django Admin 커스텀 코드 제거**
    *   **문제:** `apps/data_upload/admin.py`에는 각 모델 관리자 페이지에 파일 업로드 폼을 추가하는 지저분한 코드가 있습니다.
    *   **조치:** `DepartmentKPIAdmin`, `PublicationAdmin` 등에서 `changelist_view`를 오버라이드한 부분을 모두 삭제하십시오. 이제 Django Admin은 순수 데이터 관리용으로만 사용되며, 데이터 업로드는 우리가 만든 전용 페이지에서만 이루어집니다.

2.  **URL 및 링크 최종 정리**
    *   **조치:**
        1.  `templates/analytics/admin_dashboard.html`에 있던 깨진 링크 `<a href="/admin/data_upload/">`를 새로운 스마트 업로드 페이지 링크로 변경합니다.
            `{% url 'data_upload:upload_csv' %}`
        2.  전체 템플릿을 검토하여 하드코딩된 URL이 있다면 모두 `{% url %}` 태그로 교체합니다.

---

### **3. 결론 및 조언**

이 위기는 AI가 프로젝트의 '무엇'을 만들어야 하는지는 알았지만, '어떻게' 그리고 '왜' 만들어야 하는지에 대한 이해가 부족했기 때문에 발생했습니다. 제시해 드린 3단계 복구 전략은 단순히 버그를 수정하는 것을 넘어, **사용자 경험을 최우선으로 고려하는 올바른 아키텍처로 프로젝트를 되돌리는 과정**입니다.

다행히 핵심 로직들이 살아있어 복구는 충분히 가능합니다. 이 계획을 차근차근 실행하시면 엉망이었던 프로젝트가 다시 정상 궤도에 오를 뿐만 아니라, 훨씬 더 견고하고 사용자 친화적인 시스템으로 거듭날 것입니다. 궁금한 점이 있다면 언제든지 다시 질문해주십시오. 성공을 기원합니다.