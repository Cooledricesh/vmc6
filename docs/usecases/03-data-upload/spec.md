# Use Case Specification: 엑셀 파일 업로드

## Use Case ID
UC-03

## Use Case Name
엑셀 파일 업로드 (Excel File Upload via Django Admin)

## Actor
**Primary Actor:** 관리자 (admin role, staff/superuser)

**Secondary Actor:**
- Django Admin System
- Pandas Parser
- Database

## Description
관리자가 Django Admin 페이지를 통해 엑셀/CSV 파일을 업로드하여 학과별 KPI, 논문, 연구비, 학생 데이터를 시스템에 저장하는 프로세스. MVP 속도 극대화를 위해 별도 UI 개발 없이 Django Admin의 강력한 기본 기능을 활용한다.

## Preconditions
- 사용자가 admin 또는 staff 권한을 가지고 있다
- Django Admin 페이지에 접근할 수 있다 (`/admin`)
- 업로드할 엑셀/CSV 파일이 준비되어 있다
- 파일이 정해진 포맷을 따른다

## Postconditions
**Success:**
- 파일 데이터가 해당 테이블에 저장된다
- `upload_history` 테이블에 성공 이력이 기록된다
- 관리자에게 성공 메시지가 표시된다

**Failure:**
- 데이터가 저장되지 않는다
- `upload_history` 테이블에 실패 이력과 오류 메시지가 기록된다
- 관리자에게 상세한 오류 메시지가 표시된다

## Trigger
관리자가 Django Admin에서 파일 업로드 필드에 파일을 선택하고 "저장(Save)" 버튼 클릭

---

## Main Flow (Happy Path)

### Step 1: Django Admin 접근
**Actor:** 관리자
**Action:**
- 브라우저에서 `/admin` URL 접근
- Django Admin 로그인 (staff 또는 superuser)

**System Response:**
- Django Admin 대시보드 표시
- 사용 가능한 모델 목록 표시

### Step 2: 데이터 모델 선택
**Actor:** 관리자
**Action:**
- 업로드할 데이터 타입에 해당하는 모델 선택
  - Department KPI
  - Publications
  - Research Projects
  - Students

**System Response:**
- 해당 모델의 목록 페이지 표시
- "추가(Add)" 버튼 표시

### Step 3: 업로드 폼 접근
**Actor:** 관리자
**Action:** "추가(Add)" 버튼 클릭

**System Response:**
- Django Admin 폼 표시
- 파일 업로드 위젯 포함

### Step 4: 파일 선택 및 저장
**Actor:** 관리자
**Action:**
- "파일 선택" 버튼 클릭
- 로컬 파일 시스템에서 엑셀/CSV 파일 선택
- "저장(Save)" 버튼 클릭

### Step 5: 권한 확인
**Actor:** 시스템
**Action:**
```python
if not request.user.is_staff:
    return redirect('/admin/login/')
```

**System Response:**
- 권한 있음: 다음 단계 진행
- 권한 없음: EF-1 (권한 없음) 플로우

### Step 6: 파일 검증
**Actor:** 시스템
**Action:**
- 파일 존재 여부 확인
- 파일 확장자 검증 (.xlsx, .xls, .csv)
- 파일 크기 확인 (최대 50MB)

**System Response:**
- 검증 통과: 다음 단계
- 검증 실패: AF-1, AF-2 플로우

### Step 7: 파일 파싱
**Actor:** 시스템
**Action:**
```python
import pandas as pd

# 엑셀/CSV 읽기
if file_ext in ['.xlsx', '.xls']:
    df = pd.read_excel(file_obj)
else:
    df = pd.read_csv(file_obj, encoding='utf-8-sig')

# 컬럼명 정규화
df.columns = df.columns.str.strip()
```

**System Response:**
- DataFrame 객체 생성
- 컬럼 구조 파악

### Step 8: 스키마 검증
**Actor:** 시스템
**Action:**
- 필수 컬럼 존재 여부 확인
- 데이터 타입 검증
- 값 범위 검증 (예: 취업률 0~100)
- 중복 데이터 확인

```python
# 예: department_kpi 검증
validator = DepartmentKPIValidator(df)
errors = validator.validate()
if errors:
    raise ValidationError(errors)
```

**System Response:**
- 검증 통과: 다음 단계
- 검증 실패: AF-3 (데이터 검증 오류) 플로우

### Step 9: 데이터 저장
**Actor:** 시스템
**Action:**
```python
# 데이터 변환 및 저장
records = []
for _, row in df.iterrows():
    records.append(DepartmentKPI(
        evaluation_year=row['평가년도'],
        college=row['단과대학'],
        department=row['학과'],
        employment_rate=row['졸업생 취업률 (%)'],
        full_time_faculty=row['전임교원 수 (명)'],
        visiting_faculty=row['초빙교원 수 (명)'],
        tech_transfer_income=row['연간 기술이전 수입액 (억원)'],
        intl_conference_count=row['국제학술대회 개최 횟수']
    ))

# 일괄 저장
DepartmentKPI.objects.bulk_create(
    records,
    batch_size=1000,
    ignore_conflicts=True  # 중복 시 무시
)
```

**Database Changes:**
- 해당 테이블에 데이터 INSERT
- `upload_history` 테이블에 이력 기록

### Step 10: 업로드 이력 기록
**Actor:** 시스템
**Action:**
```python
UploadHistory.objects.create(
    user_id=request.user.id,
    file_name=uploaded_file.name,
    file_size=uploaded_file.size,
    data_type='department_kpi',
    status='success',
    rows_processed=len(df)
)
```

### Step 11: 성공 응답
**Actor:** 시스템
**System Response:**
- Django Admin 성공 메시지 표시
  - "파일 업로드 및 데이터 처리가 완료되었습니다. N건의 데이터가 저장되었습니다."
- 모델 목록 페이지로 리디렉션
- 업로드된 데이터 즉시 확인 가능

---

## Alternative Flows

### AF-1: 파일 형식 오류
**Trigger:** Step 6에서 지원하지 않는 파일 형식

**Flow:**
1. 시스템이 파일 확장자 검증 실패
2. Django Admin 폼 오류 메시지 표시
   - "지원하지 않는 파일 형식입니다. .xlsx, .xls, .csv 파일만 업로드 가능합니다."
3. 폼 유지, 사용자가 올바른 파일 선택 가능

**Return:** Step 4

### AF-2: 파일 크기 초과
**Trigger:** Step 6에서 파일 크기 50MB 초과

**Flow:**
1. 시스템이 파일 크기 검증 실패
2. Django Admin 폼 오류 메시지 표시
   - "파일 크기가 제한(50MB)을 초과했습니다."
3. 폼 유지

**Return:** Step 4

### AF-3: 데이터 검증 오류
**Trigger:** Step 8에서 스키마 또는 비즈니스 룰 검증 실패

**Flow:**
1. 시스템이 검증 오류 수집
   - 예: "3행 '졸업생 취업률' 컬럼: 숫자 형식이어야 합니다"
   - 예: "5행: 평가년도는 2000~2100 사이여야 합니다"
2. Django Admin 폼 상단에 모든 오류 표시
3. 데이터 저장하지 않음
4. `upload_history`에 실패 이력 기록
   ```python
   UploadHistory.objects.create(
       user_id=request.user.id,
       file_name=uploaded_file.name,
       file_size=uploaded_file.size,
       data_type='department_kpi',
       status='failed',
       error_message='\n'.join(errors)
   )
   ```
5. 폼 유지, 관리자가 파일 수정 후 재업로드

**Return:** Step 4

### AF-4: 빈 파일 업로드
**Trigger:** Step 7에서 파일에 데이터 행이 없음

**Flow:**
1. Pandas DataFrame이 비어있음 확인
2. 오류 메시지: "파일에 데이터가 없습니다"
3. 실패 이력 기록

**Return:** Step 4

### AF-5: 헤더 없는 파일
**Trigger:** Step 7에서 첫 행이 데이터 행으로 인식됨

**Flow:**
1. 컬럼명 불일치 감지
2. 오류 메시지: "필수 컬럼이 누락되었습니다: [컬럼명 목록]"
3. 안내: "파일 첫 행에 컬럼 헤더가 있는지 확인하세요"

**Return:** Step 4

### AF-6: 컬럼 순서 다름
**Trigger:** Step 8에서 컬럼 순서가 예상과 다름

**Flow:**
1. Pandas가 컬럼명 기반으로 자동 매핑
2. 모든 필수 컬럼이 존재하면 정상 처리
3. 순서 무관하게 데이터 저장

**Return:** Normal flow (Step 9)

---

## Exception Flows

### EF-1: 권한 없음
**Trigger:** Step 5에서 staff 권한 없음

**Flow:**
1. Django가 권한 확인
2. Django Admin 로그인 페이지로 리디렉션
3. 메시지: "이 페이지에 접근할 권한이 없습니다"

**Return:** Exit to `/admin/login/`

### EF-2: 데이터베이스 오류
**Trigger:** Step 9에서 DB INSERT 실패

**Flow:**
1. 시스템이 `DatabaseError` 감지
2. 트랜잭션 롤백 (자동)
3. 에러 로그 기록
4. Django Admin 오류 페이지 표시
5. 실패 이력 기록

**Return:** Step 4

### EF-3: 메모리 부족
**Trigger:** Step 7에서 대용량 파일 로딩 중 메모리 부족

**Flow:**
1. 시스템이 `MemoryError` 감지
2. 오류 메시지: "파일이 너무 큽니다. 데이터를 나누어 업로드하세요"
3. 실패 이력 기록

**Return:** Step 4

### EF-4: 인코딩 오류
**Trigger:** Step 7에서 CSV 파일 인코딩 문제

**Flow:**
1. Pandas가 `UnicodeDecodeError` 발생
2. 자동으로 다른 인코딩 시도 (utf-8-sig, cp949, euc-kr)
3. 모두 실패 시 오류 메시지
   - "파일 인코딩을 인식할 수 없습니다. UTF-8 또는 EUC-KR로 저장하세요"

**Return:** Step 4

---

## Business Rules

### BR-1: 지원 파일 형식
- Excel: .xlsx, .xls
- CSV: .csv (UTF-8, EUC-KR 인코딩)

### BR-2: 파일 크기 제한
- 최대 50MB
- 향후 대용량 파일은 비동기 처리 고려

### BR-3: 데이터 타입별 검증 규칙

**Department KPI:**
- 필수 컬럼: 평가년도, 단과대학, 학과, 졸업생 취업률, 전임교원 수, 초빙교원 수, 기술이전 수입액, 국제학술대회 개최 횟수
- 유니크 제약: (평가년도, 단과대학, 학과)
- 값 범위: 취업률 0~100, 교원 수 >= 0

**Publications:**
- 필수 컬럼: 논문ID, 게재일, 단과대학, 학과, 논문제목, 주저자, 학술지명, 저널등급
- 유니크 제약: 논문ID
- 저널등급: SCIE, KCI, SCOPUS, KCI후보, 기타

**Research Budget:**
- 필수 컬럼: 집행ID, 과제번호, 과제명, 연구책임자, 소속학과, 지원기관, 총연구비, 집행일자, 집행항목, 집행금액, 상태
- 두 테이블 분리 저장: research_projects, execution_records
- 트랜잭션 보장

**Students:**
- 필수 컬럼: 학번, 이름, 단과대학, 학과, 학년, 과정구분, 학적상태, 성별, 입학년도
- 유니크 제약: 학번

### BR-4: 중복 데이터 처리
- 기본: ignore_conflicts=True (중복 시 무시)
- 옵션: update_conflicts=True (중복 시 업데이트)

### BR-5: 업로드 이력 자동 기록
- 모든 업로드 시도는 이력에 기록
- 성공 시: rows_processed 기록
- 실패 시: error_message 기록

---

## Non-functional Requirements

### NFR-1: 성능
- 1,000행 파일: 10초 이내 처리
- 10,000행 파일: 2분 이내 처리
- bulk_create batch_size: 1000

### NFR-2: 신뢰성
- 트랜잭션 보장 (all-or-nothing)
- 검증 실패 시 롤백
- 부분 저장 방지

### NFR-3: 사용성
- 명확한 오류 메시지
- 오류 발생 행/컬럼 명시
- 수정 후 재업로드 가능

### NFR-4: 유지보수성
- 파서 모듈화 (apps/data_upload/parsers.py)
- 검증 로직 분리 (apps/data_upload/validators.py)
- 로그 기록

---

## Test Scenarios

### TS-1: 정상 업로드 (department_kpi)
**Given:**
- valid_department_kpi.xlsx 준비
- 10개 행, 모든 필수 컬럼 포함

**When:**
- Django Admin에서 파일 선택 및 저장

**Then:**
- 10개 레코드 저장
- upload_history에 success 기록
- 성공 메시지 표시

### TS-2: 파일 형식 오류
**When:**
- .pdf 파일 업로드 시도

**Then:**
- "지원하지 않는 파일 형식입니다" 오류
- 데이터 저장 안 됨

### TS-3: 필수 컬럼 누락
**Given:**
- 파일에 '평가년도' 컬럼 없음

**When:**
- 업로드 시도

**Then:**
- "필수 컬럼 누락: 평가년도" 오류
- 실패 이력 기록

### TS-4: 데이터 타입 오류
**Given:**
- 3행 '졸업생 취업률'에 "높음" (문자열)

**When:**
- 업로드 시도

**Then:**
- "3행 '졸업생 취업률' 컬럼: 숫자 형식이어야 합니다" 오류
- 롤백

### TS-5: 중복 데이터
**Given:**
- DB에 이미 (2025, 공과대학, 컴퓨터공학과) 존재
- 파일에 동일한 조합 포함

**When:**
- ignore_conflicts=True로 업로드

**Then:**
- 중복 행 무시
- 나머지 데이터 정상 저장

### TS-6: 연구비 CSV 업로드
**Given:**
- research_project_data.csv
- 과제 2개, 각 5개 집행 내역

**When:**
- 업로드

**Then:**
- research_projects에 2개 레코드
- execution_records에 10개 레코드
- 트랜잭션 보장

### TS-7: 빈 파일
**When:**
- 헤더만 있고 데이터 행 없는 파일

**Then:**
- "파일에 데이터가 없습니다" 오류

### TS-8: 파일 크기 초과
**When:**
- 51MB 파일 업로드

**Then:**
- "파일 크기가 제한을 초과했습니다" 오류

---

## Related Use Cases
- **UC-04:** 대시보드 조회 (업로드된 데이터 표시)
- **UC-05~08:** 각 시각화 페이지 (업로드된 데이터 활용)
- **UC-12:** 데이터 업로드 이력 조회

## Dependencies
- Django Admin
- Pandas
- PostgreSQL (Supabase)
- apps/data_upload/parsers.py
- apps/data_upload/validators.py

## References
- `/docs/userflow.md` - Section 3
- `/docs/database.md` - 모든 데이터 테이블
- `/docs/prd.md` - Section 6.1.2

## Change History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-02 | Claude Code | Initial creation based on userflow.md |

---

**Document Status:** Draft
**Last Updated:** 2025-11-02
