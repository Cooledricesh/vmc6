-- ============================================================
-- 대학교 데이터 시각화 대시보드 - 초기 스키마
-- PostgreSQL Migration Script
-- Created: 2025-11-02
-- ============================================================

-- ============================================================
-- 1. 사용자 테이블 (users)
-- ============================================================
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    position VARCHAR(100),
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'manager', 'viewer')),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'inactive')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 사용자 테이블 인덱스
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_role ON users(role);

COMMENT ON TABLE users IS '사용자 인증 및 권한 관리';
COMMENT ON COLUMN users.email IS '이메일 (로그인 ID)';
COMMENT ON COLUMN users.password IS '해싱된 비밀번호';
COMMENT ON COLUMN users.role IS '역할 (admin, manager, viewer)';
COMMENT ON COLUMN users.status IS '상태 (pending, active, inactive)';

-- ============================================================
-- 2. 업로드 이력 테이블 (upload_history)
-- ============================================================
CREATE TABLE upload_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    data_type VARCHAR(50) NOT NULL CHECK (data_type IN ('department_kpi', 'publication', 'research_budget', 'student')),
    upload_date TIMESTAMP NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'failed')),
    rows_processed INTEGER,
    error_message TEXT,
    CONSTRAINT fk_upload_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 업로드 이력 테이블 인덱스
CREATE INDEX idx_upload_user_date ON upload_history(user_id, upload_date);
CREATE INDEX idx_upload_type_status ON upload_history(data_type, status);
CREATE INDEX idx_upload_user_fk ON upload_history(user_id);

COMMENT ON TABLE upload_history IS '파일 업로드 이력 추적';
COMMENT ON COLUMN upload_history.data_type IS '데이터 타입 (department_kpi, publication, research_budget, student)';
COMMENT ON COLUMN upload_history.rows_processed IS '처리된 행 수';

-- ============================================================
-- 3. 학과별 KPI 테이블 (department_kpi)
-- ============================================================
CREATE TABLE department_kpi (
    id BIGSERIAL PRIMARY KEY,
    evaluation_year INTEGER NOT NULL,
    college VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    employment_rate NUMERIC(5,2),
    full_time_faculty INTEGER,
    visiting_faculty INTEGER,
    tech_transfer_income NUMERIC(12,2),
    intl_conference_count INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_dept_kpi_year_college_dept UNIQUE (evaluation_year, college, department)
);

-- 학과별 KPI 테이블 인덱스
CREATE INDEX idx_dept_kpi_year ON department_kpi(evaluation_year);
CREATE INDEX idx_dept_kpi_college_dept ON department_kpi(college, department);

COMMENT ON TABLE department_kpi IS '학과별 주요 성과 지표';
COMMENT ON COLUMN department_kpi.evaluation_year IS '평가년도';
COMMENT ON COLUMN department_kpi.college IS '단과대학';
COMMENT ON COLUMN department_kpi.department IS '학과';
COMMENT ON COLUMN department_kpi.employment_rate IS '졸업생 취업률 (%)';
COMMENT ON COLUMN department_kpi.full_time_faculty IS '전임교원 수 (명)';
COMMENT ON COLUMN department_kpi.visiting_faculty IS '초빙교원 수 (명)';
COMMENT ON COLUMN department_kpi.tech_transfer_income IS '연간 기술이전 수입액 (억원)';
COMMENT ON COLUMN department_kpi.intl_conference_count IS '국제학술대회 개최 횟수';

-- ============================================================
-- 4. 논문 게재 테이블 (publications)
-- ============================================================
CREATE TABLE publications (
    id BIGSERIAL PRIMARY KEY,
    publication_id VARCHAR(50) UNIQUE NOT NULL,
    publication_date DATE NOT NULL,
    college VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    title TEXT NOT NULL,
    first_author VARCHAR(100) NOT NULL,
    co_authors TEXT,
    journal_name VARCHAR(255) NOT NULL,
    journal_grade VARCHAR(20),
    impact_factor NUMERIC(5,2),
    project_linked VARCHAR(1) CHECK (project_linked IN ('Y', 'N')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 논문 게재 테이블 인덱스
CREATE INDEX idx_pub_date ON publications(publication_date);
CREATE INDEX idx_pub_college_dept ON publications(college, department);
CREATE INDEX idx_pub_first_author ON publications(first_author);
CREATE INDEX idx_pub_journal_grade ON publications(journal_grade);

COMMENT ON TABLE publications IS '논문 게재 목록 및 성과';
COMMENT ON COLUMN publications.publication_id IS '논문ID (예: PUB-23-001)';
COMMENT ON COLUMN publications.publication_date IS '게재일';
COMMENT ON COLUMN publications.college IS '단과대학';
COMMENT ON COLUMN publications.department IS '학과';
COMMENT ON COLUMN publications.title IS '논문제목';
COMMENT ON COLUMN publications.first_author IS '주저자';
COMMENT ON COLUMN publications.co_authors IS '참여저자 (세미콜론 구분)';
COMMENT ON COLUMN publications.journal_name IS '학술지명';
COMMENT ON COLUMN publications.journal_grade IS '저널등급 (SCIE, KCI 등)';
COMMENT ON COLUMN publications.impact_factor IS 'Impact Factor';
COMMENT ON COLUMN publications.project_linked IS '과제연계여부 (Y/N)';

-- ============================================================
-- 5. 연구 과제 테이블 (research_projects)
-- ============================================================
CREATE TABLE research_projects (
    id BIGSERIAL PRIMARY KEY,
    project_number VARCHAR(50) UNIQUE NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    principal_investigator VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    funding_agency VARCHAR(100) NOT NULL,
    total_budget BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 연구 과제 테이블 인덱스
CREATE INDEX idx_project_number ON research_projects(project_number);
CREATE INDEX idx_project_department ON research_projects(department);
CREATE INDEX idx_project_funding_agency ON research_projects(funding_agency);
CREATE INDEX idx_project_principal_investigator ON research_projects(principal_investigator);

COMMENT ON TABLE research_projects IS '연구 과제 기본 정보';
COMMENT ON COLUMN research_projects.project_number IS '과제번호 (예: NRF-2023-015)';
COMMENT ON COLUMN research_projects.project_name IS '과제명';
COMMENT ON COLUMN research_projects.principal_investigator IS '연구책임자';
COMMENT ON COLUMN research_projects.department IS '소속학과';
COMMENT ON COLUMN research_projects.funding_agency IS '지원기관';
COMMENT ON COLUMN research_projects.total_budget IS '총연구비 (원)';

-- ============================================================
-- 6. 연구비 집행 상세 테이블 (execution_records)
-- ============================================================
CREATE TABLE execution_records (
    id BIGSERIAL PRIMARY KEY,
    execution_id VARCHAR(50) UNIQUE NOT NULL,
    project_id BIGINT NOT NULL,
    execution_date DATE NOT NULL,
    expense_category VARCHAR(100) NOT NULL,
    amount BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('집행완료', '처리중')),
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_execution_project FOREIGN KEY (project_id) REFERENCES research_projects(id) ON DELETE CASCADE
);

-- 연구비 집행 상세 테이블 인덱스
CREATE INDEX idx_exec_project ON execution_records(project_id);
CREATE INDEX idx_exec_date ON execution_records(execution_date);
CREATE INDEX idx_exec_expense_category ON execution_records(expense_category);
CREATE INDEX idx_exec_status ON execution_records(status);
CREATE INDEX idx_exec_project_fk ON execution_records(project_id);

COMMENT ON TABLE execution_records IS '연구비 상세 집행 내역';
COMMENT ON COLUMN execution_records.execution_id IS '집행ID (예: T2301001)';
COMMENT ON COLUMN execution_records.project_id IS '과제 외래키';
COMMENT ON COLUMN execution_records.execution_date IS '집행일자';
COMMENT ON COLUMN execution_records.expense_category IS '집행항목';
COMMENT ON COLUMN execution_records.amount IS '집행금액 (원)';
COMMENT ON COLUMN execution_records.status IS '상태 (집행완료, 처리중)';
COMMENT ON COLUMN execution_records.description IS '비고';

-- ============================================================
-- 7. 학생 정보 테이블 (students)
-- ============================================================
CREATE TABLE students (
    id BIGSERIAL PRIMARY KEY,
    student_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    college VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    grade INTEGER,
    program_type VARCHAR(20),
    enrollment_status VARCHAR(20) NOT NULL CHECK (enrollment_status IN ('재학', '휴학', '졸업')),
    gender VARCHAR(10),
    admission_year INTEGER NOT NULL,
    advisor VARCHAR(100),
    email VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 학생 정보 테이블 인덱스
CREATE INDEX idx_student_college_dept ON students(college, department);
CREATE INDEX idx_student_status ON students(enrollment_status);
CREATE INDEX idx_student_admission ON students(admission_year);
CREATE INDEX idx_student_advisor ON students(advisor);
CREATE INDEX idx_student_grade_program ON students(grade, program_type);

COMMENT ON TABLE students IS '학생 명단 및 학적 정보';
COMMENT ON COLUMN students.student_number IS '학번';
COMMENT ON COLUMN students.name IS '이름';
COMMENT ON COLUMN students.college IS '단과대학';
COMMENT ON COLUMN students.department IS '학과';
COMMENT ON COLUMN students.grade IS '학년 (0: 대학원)';
COMMENT ON COLUMN students.program_type IS '과정구분 (학사, 석사)';
COMMENT ON COLUMN students.enrollment_status IS '학적상태 (재학, 휴학, 졸업)';
COMMENT ON COLUMN students.gender IS '성별 (남, 여)';
COMMENT ON COLUMN students.admission_year IS '입학년도';
COMMENT ON COLUMN students.advisor IS '지도교수';
COMMENT ON COLUMN students.email IS '이메일';

-- ============================================================
-- 8. 트리거 함수 및 트리거 생성
-- ============================================================

-- updated_at 자동 갱신 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- users 테이블 updated_at 트리거
CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- research_projects 테이블 updated_at 트리거
CREATE TRIGGER trigger_research_projects_updated_at
    BEFORE UPDATE ON research_projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- students 테이블 updated_at 트리거
CREATE TRIGGER trigger_students_updated_at
    BEFORE UPDATE ON students
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 9. 초기 데이터 삽입 (관리자 계정)
-- ============================================================

-- 기본 관리자 계정 생성 (비밀번호: admin1234, Django에서 해싱 필요)
-- 실제 운영 시에는 Django의 createsuperuser 명령어 사용 권장
INSERT INTO users (email, password, name, department, position, role, status, created_at, updated_at)
VALUES (
    'admin@university.ac.kr',
    'pbkdf2_sha256$600000$dummy$placeholder', -- Django에서 실제 해시로 교체 필요
    'System Admin',
    '기획처',
    '시스템 관리자',
    'admin',
    'active',
    NOW(),
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- ============================================================
-- 10. 뷰 생성 (집계 쿼리 최적화)
-- ============================================================

-- 연구비 집행률 뷰
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
GROUP BY p.id, p.project_number, p.project_name, p.principal_investigator, p.department, p.funding_agency, p.total_budget;

COMMENT ON VIEW v_project_execution_rate IS '연구 과제별 집행률 계산 뷰';

-- 학과별 학생 통계 뷰
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
    COUNT(*) FILTER (WHERE program_type = '석사') AS graduate_students
FROM students
GROUP BY college, department;

COMMENT ON VIEW v_department_student_stats IS '학과별 학생 통계 뷰';

-- 논문 게재 통계 뷰
CREATE OR REPLACE VIEW v_publication_stats AS
SELECT
    EXTRACT(YEAR FROM publication_date)::INTEGER AS publication_year,
    college,
    department,
    journal_grade,
    COUNT(*) AS publication_count,
    AVG(impact_factor) AS avg_impact_factor,
    COUNT(*) FILTER (WHERE project_linked = 'Y') AS project_linked_count
FROM publications
GROUP BY EXTRACT(YEAR FROM publication_date), college, department, journal_grade;

COMMENT ON VIEW v_publication_stats IS '논문 게재 통계 뷰';

-- ============================================================
-- 11. 권한 설정 (선택적)
-- ============================================================

-- 읽기 전용 역할 생성 (필요 시 사용)
-- CREATE ROLE viewer_role;
-- GRANT CONNECT ON DATABASE university_db TO viewer_role;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO viewer_role;

-- ============================================================
-- 마이그레이션 완료
-- ============================================================

-- 마이그레이션 버전 확인용 주석
-- Migration Version: 20251102000000
-- Description: Initial schema creation for university data visualization dashboard
-- Tables Created: 7 (users, upload_history, department_kpi, publications, research_projects, execution_records, students)
-- Views Created: 3 (v_project_execution_rate, v_department_student_stats, v_publication_stats)
