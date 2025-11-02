# 데이터베이스 설계 문서
## 대학교 데이터 시각화 대시보드

---

## 문서 정보
- **작성일**: 2025-11-02
- **버전**: 2.0 (개선판)
- **데이터베이스**: PostgreSQL 14+ (Supabase)
- **마이그레이션 위치**: `supabase/migrations/20251102000000_initial_schema.sql`

---

## 목차
1. [데이터플로우](#1-데이터플로우)
2. [테이블 상세 정의](#2-테이블-상세-정의)
3. [인덱스 전략](#3-인덱스-전략)
4. [집계 뷰](#4-집계-뷰)
5. [주요 쿼리 패턴](#5-주요-쿼리-패턴)
6. [데이터 검증 규칙](#6-데이터-검증-규칙)

---

## 1. 데이터플로우

### 1.1 회원가입 및 인증 플로우
```
[사용자 회원가입]
  → users 테이블 INSERT (status: 'pending')
  → 관리자 승인 대기

[관리자 승인]
  → users 테이블 UPDATE (status: 'active' or 'inactive')

[로그인]
  → users 조회 (email, status='active')
  → Django 세션 생성
  → 권한별 데이터 접근 제어
```

### 1.2 데이터 업로드 플로우

#### 일반 데이터 업로드 (department_kpi, publications, students)
```
[Django Admin 업로드]
  → 파일 검증 (형식, 크기)
  → Pandas 파싱
  → 스키마 검증 (필수 컬럼, 데이터 타입)
  → 비즈니스 규칙 검증 (범위, 중복 등)
  → 성공 시:
    - 대상 테이블에 bulk_insert
    - upload_history 기록 (status: 'success', rows_processed)
  → 실패 시:
    - 롤백
    - upload_history 기록 (status: 'failed', error_message)
```

#### 연구비 데이터 업로드 (research_project_data.csv - 특수 케이스)
```
[CSV 구조]
  - 집행ID, 과제번호, 과제명, 연구책임자, 소속학과, 지원기관, 총연구비,
    집행일자, 집행항목, 집행금액, 상태, 비고

[처리 로직]
  1단계: 과제 정보 추출 및 저장
    → 과제번호별로 그룹핑
    → research_projects 테이블에 UPSERT
      (project_number 기준 중복 시 무시 또는 업데이트)

  2단계: 집행 내역 저장
    → execution_records 테이블에 INSERT
    → project_number로 research_projects.id FK 연결

[데이터 정합성 보장]
  - 트랜잭션 사용: 과제 정보와 집행 내역 원자적 처리
  - FK 제약: execution_records.project_id → research_projects.id
  - 중복 방지: execution_id UNIQUE 제약
```

### 1.3 데이터 조회 및 시각화 플로우
```
[사용자 요청]
  → 권한 확인 (role, department)
  → 필터 조건 적용
  → 권한별 데이터 범위 제한
    - admin/manager: 전체 학과
    - viewer: 소속 학과만
  → 집계 쿼리 실행 (또는 뷰 사용)
  → Chart.js 형식으로 직렬화
  → 템플릿 렌더링
```

---

## 2. 테이블 상세 정의

### 2.1 users (사용자)
사용자 인증 및 권한 관리

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
|--------|------------|----------|------|
| id | BIGSERIAL | PRIMARY KEY | 사용자 ID (자동 증가) |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 이메일 (로그인 ID) |
| password | VARCHAR(255) | NOT NULL | Django 해싱 비밀번호 |
| name | VARCHAR(100) | NOT NULL | 사용자 이름 |
| department | VARCHAR(100) | | 소속 학과 |
| position | VARCHAR(100) | | 직책 |
| role | VARCHAR(20) | NOT NULL, CHECK | 역할 (admin, manager, viewer) |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending', CHECK | 상태 (pending, active, inactive) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 가입일시 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 수정일시 (트리거 자동 갱신) |

**제약 조건:**
```sql
CHECK (role IN ('admin', 'manager', 'viewer'))
CHECK (status IN ('pending', 'active', 'inactive'))
```

**인덱스:**
- PRIMARY KEY: id
- UNIQUE INDEX: email
- INDEX: (status, role) -- 복합 인덱스로 통합

**트리거:**
- `trigger_users_updated_at`: UPDATE 시 updated_at 자동 갱신

**Django 모델 매핑:**
```python
class User(models.Model):
    class Meta:
        db_table = 'users'
        managed = False  # Supabase가 스키마 관리
```

---

### 2.2 upload_history (업로드 이력)
파일 업로드 추적 및 감사 로그

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
|--------|------------|----------|------|
| id | BIGSERIAL | PRIMARY KEY | 이력 ID |
| user_id | BIGINT | NOT NULL, FK | 업로드한 사용자 |
| file_name | VARCHAR(255) | NOT NULL | 원본 파일명 |
| file_size | BIGINT | NOT NULL | 파일 크기 (bytes) |
| data_type | VARCHAR(50) | NOT NULL, CHECK | 데이터 타입 |
| upload_date | TIMESTAMP | NOT NULL, DEFAULT NOW() | 업로드 일시 |
| status | VARCHAR(20) | NOT NULL, CHECK | 처리 상태 (success, failed) |
| rows_processed | INTEGER | | 처리된 행 수 (성공 시) |
| error_message | TEXT | | 오류 메시지 (실패 시) |

**제약 조건:**
```sql
CHECK (data_type IN ('department_kpi', 'publication', 'research_budget', 'student'))
CHECK (status IN ('success', 'failed'))
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
```

**인덱스:**
- PRIMARY KEY: id
- INDEX: (user_id, upload_date DESC) -- 사용자별 최근 업로드 조회 최적화
- INDEX: (data_type, status) -- 데이터 타입별 상태 필터링
- INDEX: upload_date DESC -- 전체 최근 업로드 조회

**CSV 타입별 매핑:**
- `department_kpi`: department_kpi.csv
- `publication`: publication_list.csv
- `research_budget`: research_project_data.csv (과제+집행 통합)
- `student`: student_roster.csv

---

### 2.3 department_kpi (학과별 KPI)
학과별 주요 성과 지표

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
|--------|------------|----------|------|
| id | BIGSERIAL | PRIMARY KEY | KPI ID |
| evaluation_year | INTEGER | NOT NULL, CHECK | 평가년도 (2000~2100) |
| college | VARCHAR(100) | NOT NULL | 단과대학 |
| department | VARCHAR(100) | NOT NULL | 학과 |
| employment_rate | NUMERIC(5,2) | CHECK | 졸업생 취업률 (0.00~100.00%) |
| full_time_faculty | INTEGER | CHECK | 전임교원 수 (0 이상) |
| visiting_faculty | INTEGER | CHECK | 초빙교원 수 (0 이상) |
| tech_transfer_income | NUMERIC(12,2) | CHECK | 기술이전 수입액 (0 이상, 억원) |
| intl_conference_count | INTEGER | CHECK | 국제학술대회 개최 횟수 (0 이상) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성일시 |

**제약 조건:**
```sql
UNIQUE (evaluation_year, college, department) -- 연도+학과 조합 유일성
CHECK (evaluation_year BETWEEN 2000 AND 2100)
CHECK (employment_rate BETWEEN 0 AND 100)
CHECK (full_time_faculty >= 0)
CHECK (visiting_faculty >= 0)
CHECK (tech_transfer_income >= 0)
CHECK (intl_conference_count >= 0)
```

**인덱스:**
- PRIMARY KEY: id
- UNIQUE INDEX: (evaluation_year, college, department)
- INDEX: evaluation_year DESC -- 최근 연도 조회
- INDEX: (college, department) -- 학과별 조회
- INDEX: (evaluation_year, college) -- 연도별 단과대학 집계

**CSV 매핑:**
```
평가년도 → evaluation_year
단과대학 → college
학과 → department
졸업생 취업률 (%) → employment_rate
전임교원 수 (명) → full_time_faculty
초빙교원 수 (명) → visiting_faculty
연간 기술이전 수입액 (억원) → tech_transfer_income
국제학술대회 개최 횟수 → intl_conference_count
```

**샘플 데이터:**
```
2025, 공과대학, 컴퓨터공학과, 88.0, 17, 5, 13.5, 4
```

---

### 2.4 publications (논문 게재)
논문 게재 목록 및 성과

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
|--------|------------|----------|------|
| id | BIGSERIAL | PRIMARY KEY | 논문 레코드 ID |
| publication_id | VARCHAR(50) | UNIQUE, NOT NULL | 논문ID (예: PUB-23-001) |
| publication_date | DATE | NOT NULL | 게재일 |
| college | VARCHAR(100) | NOT NULL | 단과대학 |
| department | VARCHAR(100) | NOT NULL | 학과 |
| title | TEXT | NOT NULL | 논문제목 |
| first_author | VARCHAR(100) | NOT NULL | 주저자 |
| co_authors | TEXT | | 참여저자 (세미콜론 구분) |
| journal_name | VARCHAR(255) | NOT NULL | 학술지명 |
| journal_grade | VARCHAR(20) | CHECK | 저널등급 (SCIE, KCI 등) |
| impact_factor | NUMERIC(5,2) | CHECK | Impact Factor (0 이상) |
| project_linked | VARCHAR(1) | CHECK | 과제연계여부 (Y/N) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성일시 |

**제약 조건:**
```sql
CHECK (journal_grade IN ('SCIE', 'KCI', 'SCOPUS', 'KCI후보', '기타'))
CHECK (impact_factor >= 0)
CHECK (project_linked IN ('Y', 'N'))
```

**인덱스:**
- PRIMARY KEY: id
- UNIQUE INDEX: publication_id
- INDEX: publication_date DESC -- 최근 논문 조회
- INDEX: (college, department, publication_date DESC) -- 학과별 논문 추이
- INDEX: first_author -- 저자별 조회
- INDEX: journal_grade -- 등급별 필터링
- INDEX: (publication_date, journal_grade) -- 연도별 등급 집계

**CSV 매핑:**
```
논문ID → publication_id
게재일 → publication_date
단과대학 → college
학과 → department
논문제목 → title
주저자 → first_author
참여저자 → co_authors (세미콜론으로 분리)
학술지명 → journal_name
저널등급 → journal_grade
Impact Factor → impact_factor
과제연계여부 → project_linked
```

**샘플 데이터:**
```
PUB-25-001, 2025-06-15, 공과대학, 컴퓨터공학과,
Federated Learning for Privacy-Preserving AI, 이서연, 정현우,
IEEE Internet of Things Journal, SCIE, 10.6, Y
```

---

### 2.5 research_projects (연구 과제)
연구 과제 기본 정보

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
|--------|------------|----------|------|
| id | BIGSERIAL | PRIMARY KEY | 과제 레코드 ID |
| project_number | VARCHAR(50) | UNIQUE, NOT NULL | 과제번호 (예: NRF-2023-015) |
| project_name | VARCHAR(255) | NOT NULL | 과제명 |
| principal_investigator | VARCHAR(100) | NOT NULL | 연구책임자 |
| department | VARCHAR(100) | NOT NULL | 소속학과 |
| funding_agency | VARCHAR(100) | NOT NULL | 지원기관 |
| total_budget | BIGINT | NOT NULL, CHECK | 총연구비 (원, 0 초과) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성일시 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 수정일시 (트리거 자동 갱신) |

**제약 조건:**
```sql
CHECK (total_budget > 0)
```

**인덱스:**
- PRIMARY KEY: id
- UNIQUE INDEX: project_number
- INDEX: (department, funding_agency) -- 학과별 지원기관 조회
- INDEX: principal_investigator -- 연구책임자별 과제 조회
- INDEX: funding_agency -- 지원기관별 집계

**트리거:**
- `trigger_research_projects_updated_at`: UPDATE 시 updated_at 자동 갱신

**CSV 매핑 (research_project_data.csv에서 추출):**
```
과제번호 → project_number (고유키로 사용)
과제명 → project_name
연구책임자 → principal_investigator
소속학과 → department
지원기관 → funding_agency
총연구비 → total_budget
```

**업로드 로직:**
```python
# CSV의 각 행에서 과제번호로 그룹핑하여 과제 정보 추출
projects = df.groupby('과제번호').first()
for project_number, data in projects.iterrows():
    ResearchProject.objects.get_or_create(
        project_number=project_number,
        defaults={
            'project_name': data['과제명'],
            'principal_investigator': data['연구책임자'],
            'department': data['소속학과'],
            'funding_agency': data['지원기관'],
            'total_budget': data['총연구비'],
        }
    )
```

---

### 2.6 execution_records (연구비 집행 상세)
연구비 상세 집행 내역

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
|--------|------------|----------|------|
| id | BIGSERIAL | PRIMARY KEY | 집행 레코드 ID |
| execution_id | VARCHAR(50) | UNIQUE, NOT NULL | 집행ID (예: T2301001) |
| project_id | BIGINT | NOT NULL, FK | 과제 외래키 |
| execution_date | DATE | NOT NULL | 집행일자 |
| expense_category | VARCHAR(100) | NOT NULL | 집행항목 |
| amount | BIGINT | NOT NULL, CHECK | 집행금액 (원, 0 이상) |
| status | VARCHAR(20) | NOT NULL, CHECK | 상태 (집행완료, 처리중) |
| description | TEXT | | 비고 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성일시 |

**제약 조건:**
```sql
CHECK (amount >= 0)
CHECK (status IN ('집행완료', '처리중'))
FOREIGN KEY (project_id) REFERENCES research_projects(id) ON DELETE CASCADE
```

**인덱스:**
- PRIMARY KEY: id
- UNIQUE INDEX: execution_id
- INDEX: project_id -- FK 조인 최적화
- INDEX: execution_date DESC -- 최근 집행 내역 조회
- INDEX: (project_id, execution_date DESC) -- 과제별 집행 추이
- INDEX: expense_category -- 항목별 집계
- INDEX: status -- 상태별 필터링

**CSV 매핑 (research_project_data.csv에서 추출):**
```
집행ID → execution_id
과제번호 → project_id (research_projects.project_number로 FK 조회)
집행일자 → execution_date
집행항목 → expense_category
집행금액 → amount
상태 → status
비고 → description
```

**업로드 로직:**
```python
# 각 행을 execution_records에 삽입
for _, row in df.iterrows():
    # 과제번호로 project_id 조회
    project = ResearchProject.objects.get(project_number=row['과제번호'])

    ExecutionRecord.objects.create(
        execution_id=row['집행ID'],
        project=project,
        execution_date=row['집행일자'],
        expense_category=row['집행항목'],
        amount=row['집행금액'],
        status=row['상태'],
        description=row['비고'],
    )
```

**집행률 계산:**
```sql
-- 과제별 집행률
SELECT
    p.project_number,
    p.total_budget,
    COALESCE(SUM(e.amount), 0) AS total_executed,
    ROUND((COALESCE(SUM(e.amount), 0)::NUMERIC / p.total_budget * 100), 2) AS execution_rate
FROM research_projects p
LEFT JOIN execution_records e ON p.id = e.project_id
GROUP BY p.id, p.project_number, p.total_budget;
```

---

### 2.7 students (학생 정보)
학생 명단 및 학적 정보

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
|--------|------------|----------|------|
| id | BIGSERIAL | PRIMARY KEY | 학생 레코드 ID |
| student_number | VARCHAR(20) | UNIQUE, NOT NULL | 학번 |
| name | VARCHAR(100) | NOT NULL | 이름 |
| college | VARCHAR(100) | NOT NULL | 단과대학 |
| department | VARCHAR(100) | NOT NULL | 학과 |
| grade | INTEGER | CHECK | 학년 (0: 대학원, 1~4: 학부) |
| program_type | VARCHAR(20) | CHECK | 과정구분 (학사, 석사, 박사) |
| enrollment_status | VARCHAR(20) | NOT NULL, CHECK | 학적상태 (재학, 휴학, 졸업) |
| gender | VARCHAR(10) | CHECK | 성별 (남, 여) |
| admission_year | INTEGER | NOT NULL, CHECK | 입학년도 (2000~2100) |
| advisor | VARCHAR(100) | | 지도교수 |
| email | VARCHAR(255) | | 이메일 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성일시 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 수정일시 (트리거 자동 갱신) |

**제약 조건:**
```sql
CHECK (grade BETWEEN 0 AND 4)
CHECK (program_type IN ('학사', '석사', '박사'))
CHECK (enrollment_status IN ('재학', '휴학', '졸업'))
CHECK (gender IN ('남', '여'))
CHECK (admission_year BETWEEN 2000 AND 2100)
```

**인덱스:**
- PRIMARY KEY: id
- UNIQUE INDEX: student_number
- INDEX: (college, department, enrollment_status) -- 학과별 재학생 조회
- INDEX: enrollment_status -- 학적상태별 집계
- INDEX: admission_year DESC -- 입학년도별 조회
- INDEX: advisor -- 지도교수별 학생 조회
- INDEX: (grade, program_type) -- 학년별 과정 분포

**트리거:**
- `trigger_students_updated_at`: UPDATE 시 updated_at 자동 갱신

**CSV 매핑:**
```
학번 → student_number
이름 → name
단과대학 → college
학과 → department
학년 → grade
과정구분 → program_type
학적상태 → enrollment_status
성별 → gender
입학년도 → admission_year
지도교수 → advisor
이메일 → email
```

**샘플 데이터:**
```
20192101, 정현우, 공과대학, 컴퓨터공학과, 0, 석사, 재학, 남, 2024, 이서연, hwjung@university.ac.kr
```

---

## 3. 인덱스 전략

### 3.1 인덱스 설계 원칙
1. **WHERE 절 최적화**: 자주 필터링되는 컬럼에 인덱스
2. **JOIN 최적화**: FK 컬럼에 인덱스
3. **ORDER BY 최적화**: 정렬 컬럼에 DESC 인덱스
4. **복합 인덱스**: 함께 사용되는 컬럼 조합
5. **중복 제거**: 불필요한 단일 인덱스 제거

### 3.2 주요 쿼리 패턴별 인덱스

#### 대시보드 KPI 집계
```sql
-- 쿼리: 최근 연도의 전체 학과 KPI
-- 인덱스: evaluation_year DESC
SELECT * FROM department_kpi
WHERE evaluation_year = (SELECT MAX(evaluation_year) FROM department_kpi);
```

#### 학과별 필터링
```sql
-- 쿼리: 특정 학과의 최근 3년 논문
-- 인덱스: (college, department, publication_date DESC)
SELECT * FROM publications
WHERE college = '공과대학' AND department = '컴퓨터공학과'
AND publication_date >= '2023-01-01'
ORDER BY publication_date DESC;
```

#### 연구비 집행 분석
```sql
-- 쿼리: 과제별 집행 내역
-- 인덱스: (project_id, execution_date DESC)
SELECT * FROM execution_records
WHERE project_id = 1
ORDER BY execution_date DESC;
```

#### 학생 현황 조회
```sql
-- 쿼리: 학과별 재학생 수
-- 인덱스: (college, department, enrollment_status)
SELECT college, department, COUNT(*)
FROM students
WHERE enrollment_status = '재학'
GROUP BY college, department;
```

### 3.3 인덱스 유지보수

#### 인덱스 효율성 확인
```sql
-- 사용되지 않는 인덱스 확인
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND indexrelname NOT LIKE 'pg_toast%';

-- 테이블별 인덱스 크기 확인
SELECT
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## 4. 집계 뷰

### 4.1 v_project_execution_rate (연구비 집행률)
과제별 집행금액 및 집행률 계산

```sql
CREATE OR REPLACE VIEW v_project_execution_rate AS
SELECT
    p.id,
    p.project_number,
    p.project_name,
    p.principal_investigator,
    p.department,
    p.funding_agency,
    p.total_budget,
    COALESCE(SUM(e.amount), 0) AS total_executed,
    CASE
        WHEN p.total_budget > 0 THEN
            ROUND((COALESCE(SUM(e.amount), 0)::NUMERIC / p.total_budget * 100), 2)
        ELSE 0
    END AS execution_rate_percent
FROM research_projects p
LEFT JOIN execution_records e ON p.id = e.project_id
GROUP BY p.id, p.project_number, p.project_name,
         p.principal_investigator, p.department, p.funding_agency, p.total_budget;
```

**사용 예시:**
```sql
-- 집행률 80% 이상 과제 조회
SELECT * FROM v_project_execution_rate
WHERE execution_rate_percent >= 80
ORDER BY execution_rate_percent DESC;

-- 학과별 평균 집행률
SELECT department, AVG(execution_rate_percent) AS avg_rate
FROM v_project_execution_rate
GROUP BY department;
```

### 4.2 v_department_student_stats (학과별 학생 통계)
학과별 학생 수 및 분포 집계

```sql
CREATE OR REPLACE VIEW v_department_student_stats AS
SELECT
    college,
    department,
    COUNT(*) AS total_students,
    COUNT(*) FILTER (WHERE enrollment_status = '재학') AS enrolled_students,
    COUNT(*) FILTER (WHERE enrollment_status = '휴학') AS leave_students,
    COUNT(*) FILTER (WHERE enrollment_status = '졸업') AS graduated_students,
    COUNT(*) FILTER (WHERE gender = '남') AS male_students,
    COUNT(*) FILTER (WHERE gender = '여') AS female_students,
    COUNT(*) FILTER (WHERE program_type = '학사') AS undergraduate_students,
    COUNT(*) FILTER (WHERE program_type = '석사') AS graduate_students,
    COUNT(*) FILTER (WHERE program_type = '박사') AS doctoral_students
FROM students
GROUP BY college, department;
```

**사용 예시:**
```sql
-- 재학생 많은 학과 TOP 10
SELECT college, department, enrolled_students
FROM v_department_student_stats
ORDER BY enrolled_students DESC
LIMIT 10;

-- 남녀 비율 분석
SELECT
    department,
    male_students,
    female_students,
    ROUND((female_students::NUMERIC / NULLIF(total_students, 0) * 100), 2) AS female_ratio
FROM v_department_student_stats;
```

### 4.3 v_publication_stats (논문 게재 통계)
연도별, 학과별, 저널등급별 논문 통계

```sql
CREATE OR REPLACE VIEW v_publication_stats AS
SELECT
    EXTRACT(YEAR FROM publication_date)::INTEGER AS publication_year,
    college,
    department,
    journal_grade,
    COUNT(*) AS publication_count,
    AVG(impact_factor) AS avg_impact_factor,
    COUNT(*) FILTER (WHERE project_linked = 'Y') AS project_linked_count,
    COUNT(*) FILTER (WHERE project_linked = 'N') AS project_unlinked_count
FROM publications
GROUP BY EXTRACT(YEAR FROM publication_date), college, department, journal_grade;
```

**사용 예시:**
```sql
-- 2025년 SCIE 논문 수
SELECT department, publication_count
FROM v_publication_stats
WHERE publication_year = 2025 AND journal_grade = 'SCIE'
ORDER BY publication_count DESC;

-- 평균 Impact Factor가 높은 학과
SELECT department, AVG(avg_impact_factor) AS dept_avg_if
FROM v_publication_stats
WHERE journal_grade = 'SCIE'
GROUP BY department
ORDER BY dept_avg_if DESC;
```

---

## 5. 주요 쿼리 패턴

### 5.1 대시보드 전체 KPI 요약
```sql
-- 최신 연도 전체 KPI 집계
WITH latest_year AS (
    SELECT MAX(evaluation_year) AS year FROM department_kpi
)
SELECT
    COUNT(DISTINCT department) AS total_departments,
    ROUND(AVG(employment_rate), 2) AS avg_employment_rate,
    SUM(full_time_faculty) AS total_full_time_faculty,
    SUM(visiting_faculty) AS total_visiting_faculty,
    SUM(tech_transfer_income) AS total_tech_income,
    SUM(intl_conference_count) AS total_conferences
FROM department_kpi
WHERE evaluation_year = (SELECT year FROM latest_year);
```

### 5.2 학과별 연도별 KPI 추이
```sql
-- 특정 학과의 최근 3년 취업률 추이
SELECT
    evaluation_year,
    department,
    employment_rate,
    employment_rate - LAG(employment_rate) OVER (
        PARTITION BY department ORDER BY evaluation_year
    ) AS yoy_change
FROM department_kpi
WHERE department = '컴퓨터공학과'
    AND evaluation_year >= (SELECT MAX(evaluation_year) - 2 FROM department_kpi)
ORDER BY evaluation_year;
```

### 5.3 연구비 집행 분석
```sql
-- 학과별 연구비 수주 및 집행 현황
SELECT
    p.department,
    COUNT(DISTINCT p.id) AS project_count,
    SUM(p.total_budget) AS total_budget,
    SUM(e.amount) AS total_executed,
    ROUND((SUM(e.amount)::NUMERIC / NULLIF(SUM(p.total_budget), 0) * 100), 2) AS execution_rate
FROM research_projects p
LEFT JOIN execution_records e ON p.id = e.project_id
GROUP BY p.department
ORDER BY total_budget DESC;

-- 집행항목별 지출 현황
SELECT
    e.expense_category,
    COUNT(*) AS record_count,
    SUM(e.amount) AS total_amount,
    ROUND(AVG(e.amount), 0) AS avg_amount
FROM execution_records e
GROUP BY e.expense_category
ORDER BY total_amount DESC;
```

### 5.4 논문 게재 분석
```sql
-- 저널 등급별 논문 수 (최근 1년)
SELECT
    journal_grade,
    COUNT(*) AS paper_count,
    ROUND(AVG(impact_factor), 2) AS avg_impact_factor,
    COUNT(*) FILTER (WHERE project_linked = 'Y') AS linked_count
FROM publications
WHERE publication_date >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY journal_grade
ORDER BY paper_count DESC;

-- 주저자별 논문 게재 실적
SELECT
    first_author,
    COUNT(*) AS total_papers,
    COUNT(*) FILTER (WHERE journal_grade = 'SCIE') AS scie_papers,
    ROUND(AVG(impact_factor), 2) AS avg_impact_factor
FROM publications
WHERE publication_date >= '2023-01-01'
GROUP BY first_author
HAVING COUNT(*) >= 2
ORDER BY total_papers DESC, avg_impact_factor DESC;
```

### 5.5 학생 현황 분석
```sql
-- 학과별 재학생 및 휴학생 현황
SELECT
    college,
    department,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE enrollment_status = '재학') AS enrolled,
    COUNT(*) FILTER (WHERE enrollment_status = '휴학') AS on_leave,
    ROUND(COUNT(*) FILTER (WHERE enrollment_status = '휴학')::NUMERIC /
          NULLIF(COUNT(*), 0) * 100, 2) AS leave_rate
FROM students
WHERE enrollment_status IN ('재학', '휴학')
GROUP BY college, department
ORDER BY college, department;

-- 입학년도별 학생 수 추이
SELECT
    admission_year,
    COUNT(*) AS student_count,
    COUNT(*) FILTER (WHERE enrollment_status = '졸업') AS graduated,
    COUNT(*) FILTER (WHERE enrollment_status = '재학') AS still_enrolled
FROM students
GROUP BY admission_year
ORDER BY admission_year DESC;
```

---

## 6. 데이터 검증 규칙

### 6.1 CSV 업로드 시 검증 로직

#### department_kpi 검증
```python
def validate_department_kpi(df):
    """학과별 KPI 데이터 검증"""
    errors = []

    # 필수 컬럼 확인
    required_columns = ['평가년도', '단과대학', '학과', '졸업생 취업률 (%)',
                        '전임교원 수 (명)', '초빙교원 수 (명)',
                        '연간 기술이전 수입액 (억원)', '국제학술대회 개최 횟수']
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        errors.append(f"필수 컬럼 누락: {missing_cols}")
        return errors

    # 데이터 타입 검증
    if not pd.api.types.is_integer_dtype(df['평가년도']):
        errors.append("평가년도는 정수여야 합니다")

    # 값 범위 검증
    invalid_years = df[~df['평가년도'].between(2000, 2100)]
    if not invalid_years.empty:
        errors.append(f"유효하지 않은 평가년도: {invalid_years['평가년도'].tolist()}")

    invalid_rates = df[~df['졸업생 취업률 (%)'].between(0, 100)]
    if not invalid_rates.empty:
        errors.append(f"취업률은 0~100 사이여야 합니다 (행: {invalid_rates.index.tolist()})")

    # 음수 검증
    numeric_cols = ['전임교원 수 (명)', '초빙교원 수 (명)',
                    '연간 기술이전 수입액 (억원)', '국제학술대회 개최 횟수']
    for col in numeric_cols:
        if (df[col] < 0).any():
            errors.append(f"{col}은 음수일 수 없습니다")

    # 중복 검증
    duplicates = df.duplicated(subset=['평가년도', '단과대학', '학과'], keep=False)
    if duplicates.any():
        errors.append(f"중복된 데이터: {df[duplicates][['평가년도', '단과대학', '학과']].to_dict()}")

    return errors
```

#### publications 검증
```python
def validate_publications(df):
    """논문 게재 데이터 검증"""
    errors = []

    # 필수 컬럼 확인
    required_columns = ['논문ID', '게재일', '단과대학', '학과', '논문제목',
                        '주저자', '학술지명', '저널등급', 'Impact Factor', '과제연계여부']
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        errors.append(f"필수 컬럼 누락: {missing_cols}")
        return errors

    # 논문ID 유니크 검증
    if df['논문ID'].duplicated().any():
        errors.append(f"중복된 논문ID: {df[df['논문ID'].duplicated()]['논문ID'].tolist()}")

    # 날짜 형식 검증
    try:
        pd.to_datetime(df['게재일'])
    except:
        errors.append("게재일 형식 오류 (YYYY-MM-DD 형식이어야 함)")

    # 저널 등급 검증
    valid_grades = ['SCIE', 'KCI', 'SCOPUS', 'KCI후보', '기타']
    invalid_grades = df[~df['저널등급'].isin(valid_grades + ['', None])]
    if not invalid_grades.empty:
        errors.append(f"유효하지 않은 저널등급: {invalid_grades['저널등급'].unique().tolist()}")

    # Impact Factor 음수 검증
    if (df['Impact Factor'].notna() & (df['Impact Factor'] < 0)).any():
        errors.append("Impact Factor는 음수일 수 없습니다")

    # 과제연계여부 검증
    invalid_linked = df[~df['과제연계여부'].isin(['Y', 'N', '', None])]
    if not invalid_linked.empty:
        errors.append(f"과제연계여부는 Y 또는 N이어야 합니다 (행: {invalid_linked.index.tolist()})")

    return errors
```

#### research_budget 검증
```python
def validate_research_budget(df):
    """연구비 집행 데이터 검증"""
    errors = []

    # 필수 컬럼 확인
    required_columns = ['집행ID', '과제번호', '과제명', '연구책임자', '소속학과',
                        '지원기관', '총연구비', '집행일자', '집행항목', '집행금액', '상태']
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        errors.append(f"필수 컬럼 누락: {missing_cols}")
        return errors

    # 집행ID 유니크 검증
    if df['집행ID'].duplicated().any():
        errors.append(f"중복된 집행ID: {df[df['집행ID'].duplicated()]['집행ID'].tolist()}")

    # 총연구비 양수 검증
    if (df['총연구비'] <= 0).any():
        errors.append("총연구비는 0보다 커야 합니다")

    # 집행금액 음수 검증
    if (df['집행금액'] < 0).any():
        errors.append("집행금액은 음수일 수 없습니다")

    # 상태 검증
    valid_statuses = ['집행완료', '처리중']
    invalid_statuses = df[~df['상태'].isin(valid_statuses)]
    if not invalid_statuses.empty:
        errors.append(f"유효하지 않은 상태: {invalid_statuses['상태'].unique().tolist()}")

    # 날짜 형식 검증
    try:
        pd.to_datetime(df['집행일자'])
    except:
        errors.append("집행일자 형식 오류 (YYYY-MM-DD 형식이어야 함)")

    # 집행금액이 총연구비 초과하는지 과제별로 검증
    project_totals = df.groupby('과제번호').agg({
        '총연구비': 'first',
        '집행금액': 'sum'
    })
    over_budget = project_totals[project_totals['집행금액'] > project_totals['총연구비']]
    if not over_budget.empty:
        errors.append(f"예산 초과 과제: {over_budget.index.tolist()}")

    return errors
```

#### students 검증
```python
def validate_students(df):
    """학생 명단 데이터 검증"""
    errors = []

    # 필수 컬럼 확인
    required_columns = ['학번', '이름', '단과대학', '학과', '학년', '과정구분',
                        '학적상태', '성별', '입학년도']
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        errors.append(f"필수 컬럼 누락: {missing_cols}")
        return errors

    # 학번 유니크 검증
    if df['학번'].duplicated().any():
        errors.append(f"중복된 학번: {df[df['학번'].duplicated()]['학번'].tolist()}")

    # 학년 범위 검증
    invalid_grades = df[~df['학년'].between(0, 4)]
    if not invalid_grades.empty:
        errors.append(f"유효하지 않은 학년 (0~4): {invalid_grades['학년'].tolist()}")

    # 과정구분 검증
    valid_programs = ['학사', '석사', '박사']
    invalid_programs = df[~df['과정구분'].isin(valid_programs)]
    if not invalid_programs.empty:
        errors.append(f"유효하지 않은 과정구분: {invalid_programs['과정구분'].unique().tolist()}")

    # 학적상태 검증
    valid_statuses = ['재학', '휴학', '졸업']
    invalid_statuses = df[~df['학적상태'].isin(valid_statuses)]
    if not invalid_statuses.empty:
        errors.append(f"유효하지 않은 학적상태: {invalid_statuses['학적상태'].unique().tolist()}")

    # 성별 검증
    valid_genders = ['남', '여']
    invalid_genders = df[~df['성별'].isin(valid_genders + ['', None])]
    if not invalid_genders.empty:
        errors.append(f"유효하지 않은 성별: {invalid_genders['성별'].unique().tolist()}")

    # 입학년도 범위 검증
    invalid_years = df[~df['입학년도'].between(2000, 2100)]
    if not invalid_years.empty:
        errors.append(f"유효하지 않은 입학년도: {invalid_years['입학년도'].tolist()}")

    # 이메일 형식 검증 (선택 필드)
    if 'email' in df.columns:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        invalid_emails = df[df['이메일'].notna() & ~df['이메일'].str.match(email_pattern)]
        if not invalid_emails.empty:
            errors.append(f"유효하지 않은 이메일 형식 (행: {invalid_emails.index.tolist()})")

    return errors
```

### 6.2 데이터 무결성 체크 쿼리

#### 집행금액 초과 확인
```sql
-- 총연구비를 초과한 과제 확인
SELECT
    p.project_number,
    p.project_name,
    p.total_budget,
    SUM(e.amount) AS total_executed,
    SUM(e.amount) - p.total_budget AS over_budget
FROM research_projects p
LEFT JOIN execution_records e ON p.id = e.project_id
GROUP BY p.id, p.project_number, p.project_name, p.total_budget
HAVING SUM(e.amount) > p.total_budget;
```

#### 중복 데이터 확인
```sql
-- 학과별 KPI 중복 확인
SELECT evaluation_year, college, department, COUNT(*)
FROM department_kpi
GROUP BY evaluation_year, college, department
HAVING COUNT(*) > 1;

-- 논문ID 중복 확인
SELECT publication_id, COUNT(*)
FROM publications
GROUP BY publication_id
HAVING COUNT(*) > 1;
```

#### 참조 무결성 확인
```sql
-- 존재하지 않는 과제를 참조하는 집행 내역 확인
SELECT e.*
FROM execution_records e
LEFT JOIN research_projects p ON e.project_id = p.id
WHERE p.id IS NULL;

-- 존재하지 않는 사용자를 참조하는 업로드 이력 확인
SELECT u.*
FROM upload_history u
LEFT JOIN users usr ON u.user_id = usr.id
WHERE usr.id IS NULL;
```

---

## 7. 성능 최적화 가이드

### 7.1 쿼리 최적화
```sql
-- EXPLAIN ANALYZE를 사용한 쿼리 성능 분석
EXPLAIN ANALYZE
SELECT college, department, COUNT(*)
FROM students
WHERE enrollment_status = '재학'
GROUP BY college, department;

-- 인덱스 힌트가 필요한 경우
SET enable_seqscan = OFF; -- 테스트용
```

### 7.2 대량 데이터 삽입
```python
# Django ORM bulk_create 사용
records = [
    DepartmentKPI(
        evaluation_year=row['평가년도'],
        college=row['단과대학'],
        department=row['학과'],
        employment_rate=row['졸업생 취업률 (%)'],
        # ... 기타 필드
    )
    for _, row in df.iterrows()
]
DepartmentKPI.objects.bulk_create(records, batch_size=1000, ignore_conflicts=True)
```

### 7.3 파티셔닝 (향후 고려사항)
```sql
-- 데이터가 수백만 건 이상일 경우 연도별 파티셔닝 고려
-- 예: publications 테이블을 연도별로 파티셔닝
CREATE TABLE publications_2023 PARTITION OF publications
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
```

---

## 8. 백업 및 복구

### 8.1 Supabase 백업
```bash
# Supabase CLI를 통한 전체 DB 덤프
supabase db dump -f backup_$(date +%Y%m%d).sql

# 특정 테이블만 백업
pg_dump -U postgres -h 127.0.0.1 -p 54322 -t users -t upload_history -f backup_users.sql
```

### 8.2 복구
```bash
# Supabase 로컬 환경에 복구
psql -U postgres -h 127.0.0.1 -p 54322 -f backup_20251102.sql

# Supabase 프로덕션 환경에 복구 (주의!)
# Supabase 대시보드에서 수동으로 진행 권장
```

---

## 9. 마이그레이션 가이드

### 9.1 스키마 변경 프로세스
```bash
# 1. 새 마이그레이션 파일 생성
supabase migration new add_column_to_users

# 2. SQL 작성
# supabase/migrations/20251102123456_add_column_to_users.sql

# 3. 로컬 환경에서 테스트
supabase db reset

# 4. Django 모델 업데이트 (managed=False이므로 스키마 변경 없음)

# 5. 프로덕션 배포
supabase db push
```

### 9.2 롤백
```bash
# 마지막 마이그레이션 롤백
supabase db reset

# 특정 시점으로 롤백
# 수동으로 해당 마이그레이션 파일 삭제 후 reset
```

---

## 10. 보안 및 권한

### 10.1 Row Level Security (RLS) - 선택적
```sql
-- 사용자가 자신의 소속 학과 데이터만 조회하도록 제한 (선택적)
ALTER TABLE students ENABLE ROW LEVEL SECURITY;

CREATE POLICY student_department_policy ON students
    FOR SELECT
    USING (
        department = current_setting('app.user_department', true)
        OR current_setting('app.user_role', true) IN ('admin', 'manager')
    );
```

### 10.2 데이터베이스 사용자 권한
```sql
-- 읽기 전용 사용자 (viewer role)
CREATE ROLE viewer_user WITH LOGIN PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE postgres TO viewer_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO viewer_user;

-- 읽기/쓰기 사용자 (admin role)
CREATE ROLE admin_user WITH LOGIN PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin_user;
```

---

## 11. 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 1.0 | 2025-11-02 | 초안 작성 | Claude Code |
| 2.0 | 2025-11-02 | 개선판 작성<br>- 데이터플로우 명확화 (research_budget 분리 처리)<br>- CHECK 제약 조건 추가 (범위 검증)<br>- 인덱스 최적화 (복합 인덱스, DESC 인덱스)<br>- CSV 검증 로직 상세화<br>- 쿼리 패턴별 성능 최적화 가이드 추가<br>- 집계 뷰 개선 (FILTER 구문 활용)<br>- 데이터 무결성 체크 쿼리 추가 | Claude Code |

---

## 12. 참고 문서

- [PRD](./prd.md)
- [UserFlow](./userflow.md)
- [Common Modules](./common-modules.md)
- [Supabase Migration](../supabase/migrations/20251102000000_initial_schema.sql)

---

**문서 작성 완료**
