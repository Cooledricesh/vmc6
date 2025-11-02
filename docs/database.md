# 데이터베이스 설계 문서
## 대학교 데이터 시각화 대시보드

---

## 목차
1. [데이터플로우](#1-데이터플로우)
2. [데이터베이스 스키마](#2-데이터베이스-스키마)
3. [테이블 상세 정의](#3-테이블-상세-정의)
4. [인덱스 전략](#4-인덱스-전략)
5. [데이터 관계도](#5-데이터-관계도)

---

## 1. 데이터플로우

### 1.1 회원가입 및 인증 플로우
```
[사용자]
  → 회원가입 정보 입력
  → [users 테이블] 삽입 (status: 'pending')
  → 관리자 승인 대기

[관리자]
  → [users 테이블] 조회 (status: 'pending')
  → 승인/거부 처리
  → [users 테이블] 업데이트 (status: 'active' or 'inactive')

[사용자]
  → 로그인 (status: 'active'만 가능)
  → Django 세션 생성
  → 대시보드 접근
```

### 1.2 데이터 업로드 플로우
```
[관리자]
  → Django Admin 접속
  → 엑셀/CSV 파일 업로드
  → 파일 검증 (형식, 크기, 스키마)

[시스템]
  → Pandas를 통한 데이터 파싱
  → 데이터 검증 (필수 컬럼, 데이터 타입, 중복)
  → 성공 시:
    - [department_kpi / publications / research_projects / execution_records / students] 테이블 삽입
    - [upload_history] 성공 이력 기록
  → 실패 시:
    - [upload_history] 실패 이력 및 오류 메시지 기록
```

### 1.3 데이터 조회 및 시각화 플로우
```
[사용자]
  → 대시보드 또는 시각화 페이지 접근
  → 필터 조건 선택 (기간, 학과, 카테고리 등)

[시스템]
  → 사용자 권한 확인 (role, 소속학과)
  → 조건에 맞는 데이터 조회:
    - department_kpi: 학과별 KPI 집계
    - publications: 논문 게재 통계
    - research_projects + execution_records: 연구비 수주 및 집행률 계산
    - students: 학생 수 및 분포 통계
  → 데이터 집계 및 통계 계산
  → JSON 형태로 프론트엔드 전달
  → Chart.js로 시각화
```

### 1.4 연구비 집행 데이터 플로우 (특수)
```
[CSV 업로드]
  → research_project_data.csv (과제 정보 + 집행 내역 혼합)

[시스템 처리]
  1. 과제 정보 추출 (과제번호, 과제명, 연구책임자, 소속학과, 지원기관, 총연구비)
     → [research_projects] 테이블 삽입 (중복 시 무시 또는 업데이트)

  2. 집행 내역 추출 (집행ID, 과제번호, 집행일자, 집행항목, 집행금액, 상태, 비고)
     → [execution_records] 테이블 삽입
     → [research_projects.id]와 FK 연결

[시각화 시]
  → research_projects와 execution_records를 JOIN
  → 과제별 집행금액 SUM 계산
  → 집행률 = (집행금액 합계 / 총연구비 * 100) 계산
  → 학과별, 지원기관별, 집행항목별 집계
```

---

## 2. 데이터베이스 스키마

### 2.1 ERD 개요
```
users (사용자)
  ↓ (1:N)
upload_history (업로드 이력)

department_kpi (학과별 KPI) - 독립 테이블
publications (논문 게재) - 독립 테이블
students (학생 정보) - 독립 테이블

research_projects (연구 과제)
  ↓ (1:N)
execution_records (연구비 집행 상세)
```

### 2.2 테이블 목록
| 테이블명 | 설명 | 주요 용도 |
|---------|------|----------|
| users | 사용자 정보 | 인증, 권한 관리 |
| upload_history | 업로드 이력 | 데이터 업로드 추적 |
| department_kpi | 학과별 KPI 데이터 | 학과별 실적 시각화 |
| publications | 논문 게재 데이터 | 논문 성과 시각화 |
| research_projects | 연구 과제 정보 | 연구비 수주 현황 |
| execution_records | 연구비 집행 상세 | 연구비 집행 분석 |
| students | 학생 정보 | 학생 현황 시각화 |

---

## 3. 테이블 상세 정의

### 3.1 users (사용자)
사용자 인증 및 권한 관리

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
|--------|------------|----------|------|
| id | BIGSERIAL | PRIMARY KEY | 사용자 ID (자동 증가) |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 이메일 (로그인 ID) |
| password | VARCHAR(255) | NOT NULL | 해싱된 비밀번호 |
| name | VARCHAR(100) | NOT NULL | 사용자 이름 |
| department | VARCHAR(100) | | 소속 부서/학과 |
| position | VARCHAR(100) | | 직책 |
| role | VARCHAR(20) | NOT NULL | 역할 (admin, manager, viewer) |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | 상태 (pending, active, inactive) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 가입일시 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 수정일시 |

**인덱스:**
- PRIMARY KEY: id
- UNIQUE INDEX: email
- INDEX: status, role

---

### 3.2 upload_history (업로드 이력)
파일 업로드 이력 추적

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
|--------|------------|----------|------|
| id | BIGSERIAL | PRIMARY KEY | 이력 ID |
| user_id | BIGINT | NOT NULL, FK → users(id) | 업로드한 사용자 |
| file_name | VARCHAR(255) | NOT NULL | 파일명 |
| file_size | BIGINT | NOT NULL | 파일 크기 (bytes) |
| data_type | VARCHAR(50) | NOT NULL | 데이터 타입 (department_kpi, publication, research_budget, student) |
| upload_date | TIMESTAMP | NOT NULL, DEFAULT NOW() | 업로드 일시 |
| status | VARCHAR(20) | NOT NULL | 처리 상태 (success, failed) |
| rows_processed | INTEGER | | 처리된 행 수 |
| error_message | TEXT | | 오류 메시지 (실패 시) |

**인덱스:**
- PRIMARY KEY: id
- INDEX: user_id, upload_date
- INDEX: data_type, status

---

### 3.3 department_kpi (학과별 KPI)
학과별 주요 성과 지표

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
|--------|------------|----------|------|
| id | BIGSERIAL | PRIMARY KEY | KPI ID |
| evaluation_year | INTEGER | NOT NULL | 평가년도 |
| college | VARCHAR(100) | NOT NULL | 단과대학 |
| department | VARCHAR(100) | NOT NULL | 학과 |
| employment_rate | NUMERIC(5,2) | | 졸업생 취업률 (%) |
| full_time_faculty | INTEGER | | 전임교원 수 (명) |
| visiting_faculty | INTEGER | | 초빙교원 수 (명) |
| tech_transfer_income | NUMERIC(12,2) | | 연간 기술이전 수입액 (억원) |
| intl_conference_count | INTEGER | | 국제학술대회 개최 횟수 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성일시 |

**제약 조건:**
- UNIQUE (evaluation_year, college, department)

**인덱스:**
- PRIMARY KEY: id
- UNIQUE INDEX: evaluation_year, college, department
- INDEX: evaluation_year
- INDEX: college, department

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

---

### 3.4 publications (논문 게재)
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
| journal_grade | VARCHAR(20) | | 저널등급 (SCIE, KCI 등) |
| impact_factor | NUMERIC(5,2) | | Impact Factor |
| project_linked | VARCHAR(1) | | 과제연계여부 (Y/N) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성일시 |

**인덱스:**
- PRIMARY KEY: id
- UNIQUE INDEX: publication_id
- INDEX: publication_date
- INDEX: college, department
- INDEX: first_author
- INDEX: journal_grade

**CSV 매핑:**
```
논문ID → publication_id
게재일 → publication_date
단과대학 → college
학과 → department
논문제목 → title
주저자 → first_author
참여저자 → co_authors
학술지명 → journal_name
저널등급 → journal_grade
Impact Factor → impact_factor
과제연계여부 → project_linked
```

---

### 3.5 research_projects (연구 과제)
연구 과제 기본 정보

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
|--------|------------|----------|------|
| id | BIGSERIAL | PRIMARY KEY | 과제 레코드 ID |
| project_number | VARCHAR(50) | UNIQUE, NOT NULL | 과제번호 (예: NRF-2023-015) |
| project_name | VARCHAR(255) | NOT NULL | 과제명 |
| principal_investigator | VARCHAR(100) | NOT NULL | 연구책임자 |
| department | VARCHAR(100) | NOT NULL | 소속학과 |
| funding_agency | VARCHAR(100) | NOT NULL | 지원기관 |
| total_budget | BIGINT | NOT NULL | 총연구비 (원) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성일시 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 수정일시 |

**인덱스:**
- PRIMARY KEY: id
- UNIQUE INDEX: project_number
- INDEX: department
- INDEX: funding_agency
- INDEX: principal_investigator

**CSV 매핑 (research_project_data.csv에서 추출):**
```
과제번호 → project_number
과제명 → project_name
연구책임자 → principal_investigator
소속학과 → department
지원기관 → funding_agency
총연구비 → total_budget
```

---

### 3.6 execution_records (연구비 집행 상세)
연구비 상세 집행 내역

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
|--------|------------|----------|------|
| id | BIGSERIAL | PRIMARY KEY | 집행 레코드 ID |
| execution_id | VARCHAR(50) | UNIQUE, NOT NULL | 집행ID (예: T2301001) |
| project_id | BIGINT | NOT NULL, FK → research_projects(id) | 과제 외래키 |
| execution_date | DATE | NOT NULL | 집행일자 |
| expense_category | VARCHAR(100) | NOT NULL | 집행항목 |
| amount | BIGINT | NOT NULL | 집행금액 (원) |
| status | VARCHAR(20) | NOT NULL | 상태 (집행완료, 처리중) |
| description | TEXT | | 비고 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성일시 |

**인덱스:**
- PRIMARY KEY: id
- UNIQUE INDEX: execution_id
- INDEX: project_id
- INDEX: execution_date
- INDEX: expense_category
- INDEX: status

**CSV 매핑:**
```
집행ID → execution_id
과제번호 → project_id (research_projects 테이블과 JOIN)
집행일자 → execution_date
집행항목 → expense_category
집행금액 → amount
상태 → status
비고 → description
```

**집행률 계산 쿼리:**
```sql
SELECT
  p.project_number,
  p.project_name,
  p.total_budget,
  SUM(e.amount) as total_executed,
  (SUM(e.amount)::NUMERIC / p.total_budget * 100) as execution_rate
FROM research_projects p
LEFT JOIN execution_records e ON p.id = e.project_id
GROUP BY p.id, p.project_number, p.project_name, p.total_budget;
```

---

### 3.7 students (학생 정보)
학생 명단 및 학적 정보

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
|--------|------------|----------|------|
| id | BIGSERIAL | PRIMARY KEY | 학생 레코드 ID |
| student_number | VARCHAR(20) | UNIQUE, NOT NULL | 학번 |
| name | VARCHAR(100) | NOT NULL | 이름 |
| college | VARCHAR(100) | NOT NULL | 단과대학 |
| department | VARCHAR(100) | NOT NULL | 학과 |
| grade | INTEGER | | 학년 (0: 대학원) |
| program_type | VARCHAR(20) | | 과정구분 (학사, 석사) |
| enrollment_status | VARCHAR(20) | NOT NULL | 학적상태 (재학, 휴학, 졸업) |
| gender | VARCHAR(10) | | 성별 (남, 여) |
| admission_year | INTEGER | NOT NULL | 입학년도 |
| advisor | VARCHAR(100) | | 지도교수 |
| email | VARCHAR(255) | | 이메일 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성일시 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 수정일시 |

**인덱스:**
- PRIMARY KEY: id
- UNIQUE INDEX: student_number
- INDEX: college, department
- INDEX: enrollment_status
- INDEX: admission_year
- INDEX: advisor
- INDEX: grade, program_type

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

---

## 4. 인덱스 전략

### 4.1 조회 성능 최적화
```sql
-- 대시보드 KPI 집계 (연도별, 학과별 조회 빈번)
CREATE INDEX idx_dept_kpi_year ON department_kpi(evaluation_year);
CREATE INDEX idx_dept_kpi_college_dept ON department_kpi(college, department);

-- 논문 게재 현황 (날짜, 학과, 저널등급 필터링 빈번)
CREATE INDEX idx_pub_date ON publications(publication_date);
CREATE INDEX idx_pub_college_dept ON publications(college, department);
CREATE INDEX idx_pub_journal_grade ON publications(journal_grade);

-- 연구비 집행 분석 (과제별, 날짜별, 상태별 조회)
CREATE INDEX idx_exec_project ON execution_records(project_id);
CREATE INDEX idx_exec_date ON execution_records(execution_date);
CREATE INDEX idx_exec_status ON execution_records(status);

-- 학생 현황 (학과별, 학적상태별, 입학년도별 조회)
CREATE INDEX idx_student_college_dept ON students(college, department);
CREATE INDEX idx_student_status ON students(enrollment_status);
CREATE INDEX idx_student_admission ON students(admission_year);

-- 업로드 이력 (사용자별, 날짜별 조회)
CREATE INDEX idx_upload_user_date ON upload_history(user_id, upload_date);
CREATE INDEX idx_upload_type_status ON upload_history(data_type, status);
```

### 4.2 외래키 인덱스
```sql
-- 외래키 조인 성능 향상
CREATE INDEX idx_upload_user_fk ON upload_history(user_id);
CREATE INDEX idx_exec_project_fk ON execution_records(project_id);
```

---

## 5. 데이터 관계도

### 5.1 관계 요약
```
users (1) ─────── (N) upload_history
  id                    user_id

research_projects (1) ─────── (N) execution_records
  id                            project_id

독립 테이블:
- department_kpi
- publications
- students
```

### 5.2 제약 조건
```sql
-- 외래키 제약
ALTER TABLE upload_history
  ADD CONSTRAINT fk_upload_user
  FOREIGN KEY (user_id) REFERENCES users(id)
  ON DELETE CASCADE;

ALTER TABLE execution_records
  ADD CONSTRAINT fk_execution_project
  FOREIGN KEY (project_id) REFERENCES research_projects(id)
  ON DELETE CASCADE;

-- 유니크 제약
ALTER TABLE department_kpi
  ADD CONSTRAINT uq_dept_kpi_year_college_dept
  UNIQUE (evaluation_year, college, department);
```

### 5.3 트리거 (자동 업데이트)
```sql
-- updated_at 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_research_projects_updated_at
  BEFORE UPDATE ON research_projects
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_students_updated_at
  BEFORE UPDATE ON students
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## 6. 데이터 삽입 예시

### 6.1 CSV 업로드 시 데이터 처리 로직

**department_kpi.csv 업로드:**
```python
import pandas as pd

df = pd.read_csv('department_kpi.csv')

for _, row in df.iterrows():
    DepartmentKPI.objects.update_or_create(
        evaluation_year=row['평가년도'],
        college=row['단과대학'],
        department=row['학과'],
        defaults={
            'employment_rate': row['졸업생 취업률 (%)'],
            'full_time_faculty': row['전임교원 수 (명)'],
            'visiting_faculty': row['초빙교원 수 (명)'],
            'tech_transfer_income': row['연간 기술이전 수입액 (억원)'],
            'intl_conference_count': row['국제학술대회 개최 횟수'],
        }
    )
```

**research_project_data.csv 업로드 (과제 + 집행 분리):**
```python
import pandas as pd

df = pd.read_csv('research_project_data.csv')

for _, row in df.iterrows():
    # 1. 과제 정보 삽입 (중복 시 무시)
    project, created = ResearchProject.objects.get_or_create(
        project_number=row['과제번호'],
        defaults={
            'project_name': row['과제명'],
            'principal_investigator': row['연구책임자'],
            'department': row['소속학과'],
            'funding_agency': row['지원기관'],
            'total_budget': row['총연구비'],
        }
    )

    # 2. 집행 내역 삽입
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

---

## 7. 주요 쿼리 패턴

### 7.1 대시보드 KPI 집계
```sql
-- 최신 연도의 전체 KPI 요약
SELECT
  COUNT(DISTINCT department) as total_departments,
  AVG(employment_rate) as avg_employment_rate,
  SUM(full_time_faculty) as total_faculty,
  SUM(tech_transfer_income) as total_tech_income,
  SUM(intl_conference_count) as total_conferences
FROM department_kpi
WHERE evaluation_year = (SELECT MAX(evaluation_year) FROM department_kpi);
```

### 7.2 연도별 추이 분석
```sql
-- 학과별 취업률 추이 (최근 3년)
SELECT
  evaluation_year,
  department,
  employment_rate
FROM department_kpi
WHERE evaluation_year >= (SELECT MAX(evaluation_year) - 2 FROM department_kpi)
  AND department = '컴퓨터공학과'
ORDER BY evaluation_year;
```

### 7.3 논문 게재 통계
```sql
-- 저널 등급별 논문 수 (최근 1년)
SELECT
  journal_grade,
  COUNT(*) as paper_count,
  AVG(impact_factor) as avg_impact_factor
FROM publications
WHERE publication_date >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY journal_grade
ORDER BY paper_count DESC;
```

### 7.4 연구비 집행률 분석
```sql
-- 학과별 연구비 수주 및 집행 현황
SELECT
  p.department,
  COUNT(DISTINCT p.id) as project_count,
  SUM(p.total_budget) as total_budget,
  SUM(e.amount) as total_executed,
  (SUM(e.amount)::NUMERIC / SUM(p.total_budget) * 100) as execution_rate
FROM research_projects p
LEFT JOIN execution_records e ON p.id = e.project_id
GROUP BY p.department
ORDER BY total_budget DESC;
```

### 7.5 학생 현황 통계
```sql
-- 학과별 재학생 수 및 학년 분포
SELECT
  college,
  department,
  enrollment_status,
  COUNT(*) as student_count
FROM students
WHERE enrollment_status IN ('재학', '휴학')
GROUP BY college, department, enrollment_status
ORDER BY college, department;
```

---

## 8. 데이터 백업 및 유지보수

### 8.1 정기 백업
```sql
-- PostgreSQL 백업 명령어
pg_dump -U username -h localhost -F c -b -v -f backup_$(date +%Y%m%d).dump database_name
```

### 8.2 데이터 정합성 체크
```sql
-- 연구비 집행액이 총연구비를 초과하는 과제 확인
SELECT
  p.project_number,
  p.project_name,
  p.total_budget,
  SUM(e.amount) as total_executed
FROM research_projects p
LEFT JOIN execution_records e ON p.id = e.project_id
GROUP BY p.id, p.project_number, p.project_name, p.total_budget
HAVING SUM(e.amount) > p.total_budget;
```

### 8.3 성능 모니터링
```sql
-- 느린 쿼리 확인 (PostgreSQL)
SELECT
  query,
  calls,
  total_time,
  mean_time,
  max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

---

## 9. 보안 및 권한 관리

### 9.1 데이터베이스 사용자 권한
```sql
-- 읽기 전용 사용자 (viewer role)
CREATE USER viewer_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE university_db TO viewer_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO viewer_user;

-- 관리자 사용자 (admin role)
CREATE USER admin_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin_user;
```

### 9.2 Row Level Security (RLS)
```sql
-- 사용자가 자신의 소속 학과 데이터만 조회하도록 제한 (선택적)
ALTER TABLE students ENABLE ROW LEVEL SECURITY;

CREATE POLICY student_department_policy ON students
  FOR SELECT
  USING (department = current_setting('app.user_department', true));
```

---

## 10. 문서 메타 정보

- **문서 작성일**: 2025-11-02
- **데이터베이스**: PostgreSQL 14+
- **작성자**: Claude Code
- **관련 문서**:
  - [PRD](./prd.md)
  - [Requirements](./requirements.md)
  - [UserFlow](./userflow.md)

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.0 | 2025-11-02 | 초안 작성 - 7개 테이블 정의 및 데이터플로우 설계 |
