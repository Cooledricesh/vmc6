# Use Cases Summary - University Data Visualization Dashboard

## Executive Summary

This document provides a comprehensive summary of all 12 use cases for the University Data Visualization Dashboard system. Each use case represents a critical user interaction flow documented in detail in individual specification files.

---

## UC-01: 회원가입 (User Registration)

**Status:** ✅ Complete - [Full Spec](./01-signup/spec.md)

**Primary Actor:** 신규 사용자

**Key Flow:**
1. 사용자가 회원가입 페이지 접근
2. 필수 정보 입력 (이름, 이메일, 비밀번호, 소속 부서, 직책)
3. 시스템이 입력값 검증 (이메일 형식, 비밀번호 정책, 중복 확인)
4. 사용자 정보 저장 (status='pending', role='viewer')
5. 관리자 승인 대기 안내 표시

**Critical Business Rules:**
- 이메일 유일성 보장
- 비밀번호 최소 4자 (PBKDF2 해싱)
- 신규 가입 시 'pending' 상태로 생성
- 관리자 승인 필요

---

## UC-02: 로그인 (User Login)

**Status:** ✅ Complete - [Full Spec](./02-login/spec.md)

**Primary Actor:** 등록된 사용자 (status='active')

**Key Flow:**
1. 이메일과 비밀번호 입력
2. 시스템이 사용자 인증 (이메일 조회 → 비밀번호 검증)
3. 사용자 상태 확인 (active/pending/inactive)
4. Django 세션 생성 (sessionid 쿠키)
5. 대시보드로 리디렉션

**Alternative Flows:**
- 승인 대기 상태 (pending): 로그인 불가, 안내 메시지
- 비활성화 상태 (inactive): 로그인 불가, 관리자 문의 안내
- 인증 실패: 일반적 오류 메시지 (보안)

**Critical Business Rules:**
- Django 세션 기반 인증 (MVP)
- status='active'만 로그인 가능
- 로그인 실패 시 구체적 오류 노출 금지

---

## UC-03: 엑셀 파일 업로드 (Excel File Upload via Django Admin)

**Status:** ✅ Complete - [Full Spec](./03-data-upload/spec.md)

**Primary Actor:** 관리자 (admin/staff)

**Key Flow:**
1. Django Admin 페이지 (`/admin`) 접근
2. 해당 데이터 모델 선택 (Department KPI, Publications, Research Projects, Students)
3. "추가(Add)" 버튼 클릭
4. 파일 선택 및 "저장(Save)" 클릭
5. 시스템이 파일 검증 (형식, 크기, 스키마)
6. Pandas로 파일 파싱
7. 데이터 검증 (필수 컬럼, 데이터 타입, 범위, 중복)
8. bulk_create로 일괄 저장
9. upload_history에 이력 기록

**Supported Data Types:**
- **department_kpi**: 학과별 KPI (취업률, 교원 수, 기술이전, 학술대회)
- **publications**: 논문 게재 목록
- **research_budget**: 연구비 집행 데이터 (2-table split: projects + execution_records)
- **students**: 학생 명단

**Critical Business Rules:**
- 파일 형식: .xlsx, .xls, .csv
- 최대 크기: 50MB
- 트랜잭션 보장 (all-or-nothing)
- 검증 실패 시 전체 롤백

---

## UC-04: 대시보드 조회 (Dashboard View)

**Primary Actor:** 로그인된 사용자

**Key Flow:**
1. 대시보드 페이지 (`/dashboard`) 접근
2. 권한 확인 및 데이터 접근 범위 결정
   - Admin/Manager: 전체 데이터
   - Viewer: 소속 학과만
3. 최근 데이터 조회 및 KPI 계산
   - 학과별 KPI 집계
   - 논문 게재 수
   - 학생 수
   - 연구비 집행 현황
4. 추이 데이터 계산 (최근 3개년, 전년 대비 증감률)
5. 4개 KPI 요약 카드 렌더링
6. 주요 추이 그래프 표시 (Chart.js)
7. 최근 업데이트 정보 표시
8. 빠른 이동 메뉴 제공

**Key Metrics Displayed:**
- 평균 취업률, 총 교원 수, 기술이전 수입액, 총 학술대회 개최 횟수
- 논문 총 게재 수
- 재학생 총 인원
- 총 연구비 및 평균 집행률

**Critical Business Rules:**
- Role-based data filtering
- 기본값: 최근 학기 또는 최근 연도
- 데이터 없을 시 안내 메시지 표시

---

## UC-05: 학과별 KPI 데이터 시각화 (Department KPI Visualization)

**Primary Actor:** 로그인된 사용자

**Key Flow:**
1. KPI 시각화 페이지 (`/analytics/department-kpi`) 접근
2. 필터 옵션 선택
   - 평가년도 (단일/범위)
   - 단과대학
   - 학과 (단일/복수)
   - KPI 지표 선택
3. 권한별 데이터 범위 제한 적용
4. 데이터 조회 및 집계
   - 학과별, 단과대학별, 연도별 집계
5. 통계 계산
   - 평균, 최고/최저, 증감률
6. Chart.js 데이터 포맷팅
7. 시각화 차트 렌더링
   - 학과별 취업률 비교 (막대 그래프)
   - 학과별 교원 현황 (누적 막대)
   - 기술이전 수입액 (막대 그래프)
   - 연도별 KPI 추이 (라인 차트)
   - 단과대학별 KPI 비교 (그룹 막대)
8. 데이터 테이블 뷰 제공 (토글)

**Chart Types:**
- 막대 그래프 (Bar Chart)
- 라인 차트 (Line Chart)
- 누적 막대 그래프 (Stacked Bar)

**Critical Features:**
- 필터링 (연도, 대학, 학과, 지표)
- 차트 타입 전환
- 데이터 내보내기 (CSV, Excel)
- 차트 이미지 저장

---

## UC-06: 논문 게재 데이터 시각화 (Publications Visualization)

**Primary Actor:** 로그인된 사용자

**Key Flow:**
1. 논문 시각화 페이지 (`/analytics/publications`) 접근
2. 필터 옵션 선택
   - 게재일 기간
   - 단과대학/학과
   - 저널 등급 (SCIE, KCI 등)
   - 주저자명 검색
   - 과제연계여부
3. 데이터 조회 및 집계
   - 학과별, 연도별, 저널 등급별, 주저자별 집계
4. 통계 계산
   - 총 논문 수
   - 저널 등급별 분포
   - 평균 Impact Factor (SCIE 대상)
   - 과제연계 논문 비율
5. 시각화 차트 렌더링
   - 학과별 논문 게재 수 (막대)
   - 연도별 논문 추이 (라인)
   - 저널 등급별 분포 (파이)
   - 주저자별 게재 현황 (막대, 상위 10명)
   - 과제연계 vs 비연계 (파이)
   - Impact Factor 분포 (히스토그램/박스 플롯)

**Chart Types:**
- 막대 그래프, 라인 차트, 파이 차트
- 히스토그램, 박스 플롯

**Critical Features:**
- 저널 등급 필터링
- 주저자 검색
- Impact Factor 통계
- 과제연계 분석

---

## UC-07: 연구비 집행 데이터 시각화 (Research Budget Visualization)

**Primary Actor:** 로그인된 사용자

**Key Flow:**
1. 연구비 시각화 페이지 (`/analytics/research-budget`) 접근
2. 필터 옵션 선택
   - 집행일자 기간
   - 소속학과
   - 지원기관
   - 연구책임자명 검색
   - 집행항목
   - 집행상태
3. 데이터 조회 및 집계
   - 학과별, 지원기관별, 집행항목별, 과제별 집계
4. 통계 계산
   - 총 연구비, 총 집행금액
   - 평균 집행률 (집행금액/총연구비 * 100)
   - 학과별 연구비 수주 현황
   - 지원기관별 연구비 분포
   - 집행항목별 지출 현황
5. 시각화 차트 렌더링
   - 학과별 연구비 수주 현황 (막대)
   - 지원기관별 연구비 분포 (파이/도넛)
   - 집행항목별 지출 현황 (막대)
   - 연도별 연구비 수주 및 집행 추이 (듀얼 축 라인)
   - 연구책임자별 연구비 현황 (막대, 상위 10명)
   - 과제별 집행률 (막대/히트맵)
   - 집행상태별 분포 (파이)

**Data Model:**
- `research_projects`: 과제 기본 정보
- `execution_records`: 상세 집행 내역
- `v_project_execution_rate`: 집행률 계산 뷰

**Critical Features:**
- 집행률 계산 및 시각화
- 집행항목별 분석
- 지원기관별 통계
- 과제별 상세 집행 현황

---

## UC-08: 학생 데이터 시각화 (Students Visualization)

**Primary Actor:** 로그인된 사용자

**Key Flow:**
1. 학생 시각화 페이지 (`/analytics/students`) 접근
2. 필터 옵션 선택
   - 입학년도
   - 단과대학/학과
   - 학년 (0: 대학원, 1~4: 학부)
   - 과정구분 (학사, 석사, 박사)
   - 학적상태 (재학, 휴학, 졸업)
   - 성별
   - 지도교수명 검색
3. 데이터 조회 및 집계
   - 학과별, 학년별, 과정별, 학적상태별, 성별, 입학년도별, 지도교수별 집계
4. 통계 계산
   - 총 학생 수
   - 재학률, 휴학률
   - 성별 분포
   - 지도교수별 지도 학생 수
5. 시각화 차트 렌더링
   - 학과별 재학생 수 (막대)
   - 학년별 분포 (파이/도넛)
   - 과정구분별 분포 (파이)
   - 학적상태별 분포 (파이/막대)
   - 입학년도별 학생 수 추이 (라인)
   - 성별 분포 (파이)
   - 지도교수별 지도 학생 수 (막대, 상위 10명)
   - 학과별 학년 분포 (누적 막대)

**Chart Types:**
- 막대 그래프, 라인 차트, 파이 차트, 누적 막대

**Critical Features:**
- 학적상태 필터링
- 과정구분 분석
- 재학률/휴학률 계산
- 지도교수별 통계

---

## UC-09: 관리자 - 사용자 승인/거부 (User Approval Management)

**Primary Actor:** 관리자 (admin role)

**Key Flow:**
1. Django Admin 페이지 (`/admin`) 접근
2. 사용자 목록 탭 선택
3. 필터 옵션 선택 (전체, 승인 대기, 활성, 비활성)
   - 기본값: 승인 대기(pending) 상태
4. 특정 사용자 선택
5. 승인 또는 거부 버튼 클릭
6. **승인 시:**
   - 사용자 status를 'active'로 변경
   - 변경 일시 및 승인자 기록
7. **거부 시:**
   - 거부 사유 입력 (필수)
   - 사용자 status를 'inactive'로 변경
   - 거부 사유, 변경 일시, 거부자 기록
8. 데이터베이스 업데이트
9. 관리 로그 기록
10. 사용자 목록 자동 갱신

**Critical Business Rules:**
- admin role만 승인/거부 가능
- 거부 시 거부 사유 필수 입력
- 승인자/거부자 추적 기록
- 자기 자신 승인/거부 불가

**Alternative Flows:**
- 이미 처리된 사용자: 현재 상태 표시 및 안내
- 동시 처리: 먼저 처리한 관리자의 작업 우선

---

## UC-10: 사용자 프로필 관리 (Profile Management)

**Primary Actor:** 로그인된 사용자

**Key Flow:**
1. 프로필 페이지 (`/profile`) 접근
2. 현재 사용자 정보 조회 및 표시
   - 이메일 (읽기 전용)
   - 이름
   - 소속 부서
   - 직책
   - role (읽기 전용)
   - 가입일 (읽기 전용)
3. 탭 선택 (개인정보 수정 / 비밀번호 변경)

**개인정보 수정 Flow:**
1. 이름, 소속 부서, 직책 수정
2. 입력값 검증 (필수 항목, 길이 제한)
3. 변경 사항 확인
4. 데이터베이스 업데이트
5. 성공 메시지 표시 및 페이지 갱신

**비밀번호 변경 Flow:**
1. 현재 비밀번호 입력
2. 새 비밀번호 입력
3. 새 비밀번호 확인 입력
4. 검증
   - 현재 비밀번호 일치 확인
   - 새 비밀번호 정책 검증 (최소 4자)
   - 새 비밀번호 일치 확인
   - 현재와 동일한지 확인
5. 비밀번호 해싱 후 업데이트
6. 비밀번호 변경 일시 기록
7. 성공 메시지 표시 및 필드 초기화
8. 선택적: 자동 로그아웃 및 재로그인 안내

**Critical Business Rules:**
- 이메일 변경 불가
- role 변경 불가 (관리자만 가능)
- 비밀번호 변경 시 현재 비밀번호 검증 필수
- 새 비밀번호가 현재와 동일 시 경고

---

## UC-11: 로그아웃 (Logout)

**Primary Actor:** 로그인된 사용자

**Key Flow:**
1. 네비게이션 바의 사용자 메뉴 클릭
2. 로그아웃 버튼 클릭
3. 확인 팝업 표시 (선택적)
4. 확인 버튼 클릭
5. Django 세션 종료
   - 세션 쿠키 삭제
   - 서버 측 세션 데이터 제거
6. 애플리케이션 전역 상태 초기화
7. 로그아웃 시간 기록 (선택적)
8. 로그인 페이지 (`/login`)로 리디렉션

**Critical Business Rules:**
- Django 세션 기반 로그아웃 (MVP)
- 클라이언트 측 세션 쿠키 삭제
- 서버 측 세션 invalidation

**Alternative Flows:**
- 이미 로그아웃 상태: 로그인 페이지로 리디렉션
- 여러 탭에서 동시 로그인: 한 탭 로그아웃 시 모든 탭 로그아웃

**Edge Cases:**
- 로그아웃 중 네트워크 끊김: 클라이언트 측 쿠키 삭제 후 로그인 페이지 이동
- 뒤로가기로 이전 페이지 접근 시도: 세션 없으면 로그인 페이지로 리디렉션
- 작업 중인 데이터: 확인 팝업으로 저장되지 않은 작업 경고

---

## UC-12: 데이터 업로드 이력 조회 (Upload History View)

**Primary Actor:** 로그인된 사용자

**Key Flow:**
1. 데이터 히스토리 페이지 (`/data/history`) 접근
2. 필터 옵션 선택
   - 업로드 기간 (시작일, 종료일)
   - 데이터 타입 (전체, KPI, 논문, 연구비, 학생)
   - 업로드 상태 (전체, 성공, 실패)
   - 업로드자 검색 (관리자만)
3. 권한별 데이터 범위 제한
   - 일반 사용자: 본인의 업로드 이력만
   - 관리자: 전체 이력
4. 업로드 이력 조회 (`upload_history` 테이블)
5. 이력 정보 집계
   - 총 업로드 건수
   - 성공/실패 건수 및 비율
   - 데이터 타입별 업로드 건수
   - 총 업로드된 데이터 행 수
6. 업로드 이력 목록 테이블 렌더링
   - 업로드 일시, 파일명, 데이터 타입, 업로드자, 상태, 저장된 행 수
   - 상태별 색상 표시 (성공: 녹색, 실패: 빨간색)
7. 통계 차트 표시
   - 데이터 타입별 통계 (파이)
   - 시간별 업로드 추이 (라인)

**상세 정보 조회 Flow:**
1. 특정 이력 항목 클릭
2. 상세 정보 모달/패널 표시
   - 파일명, 파일 크기, 업로드 일시
   - 업로드자 정보
   - 데이터 타입
   - 처리 결과 (성공/실패)
   - **성공 시:** 저장된 데이터 행 수, 데이터 미리보기
   - **실패 시:** 오류 메시지, 오류 로그 다운로드 버튼
3. 액션 버튼
   - 동일 파일 재업로드
   - 해당 데이터 시각화 페이지로 이동 (성공한 경우)

**Critical Business Rules:**
- Role-based access: viewer는 본인 이력만, admin은 전체 조회
- 기본 필터: 최근 1개월
- 페이지네이션 지원

---

## Common Patterns Across All Use Cases

### 1. Authentication & Authorization
- 모든 기능은 로그인 필요 (`@login_required`)
- Role-based access control
  - admin: 모든 기능 접근
  - manager: 전체 데이터 조회
  - viewer: 소속 학과 데이터만 조회
- Django 세션 기반 인증 (MVP)

### 2. Data Access Patterns
```python
# 권한별 데이터 필터링 공통 패턴
def get_accessible_departments(user):
    if user.role in ['admin', 'manager']:
        return Department.objects.all()
    else:
        return Department.objects.filter(name=user.department)
```

### 3. Error Handling
- 명확하고 실행 가능한 오류 메시지
- 보안상 구체적 정보 노출 금지 (로그인 실패 등)
- 에러 로그 기록
- 사용자 친화적 오류 페이지

### 4. Performance Requirements
- 페이지 로딩: 3초 이내
- 차트 렌더링: 1초 이내
- 데이터베이스 쿼리 최적화 (인덱스 활용)

### 5. Security Requirements
- HTTPS 통신 필수
- CSRF 보호 (Django 기본 미들웨어)
- XSS 방지 (템플릿 자동 이스케이프)
- SQL Injection 방지 (Django ORM)
- 비밀번호 해싱 (PBKDF2)

---

## Implementation Priority

### Phase 1 (MVP) - Completed
1. ✅ UC-01: 회원가입
2. ✅ UC-02: 로그인
3. ✅ UC-03: 엑셀 파일 업로드

### Phase 2 - Core Features
4. UC-04: 대시보드 조회
5. UC-05: 학과별 KPI 데이터 시각화
6. UC-09: 관리자 - 사용자 승인/거부

### Phase 3 - Extended Visualization
7. UC-06: 논문 게재 데이터 시각화
8. UC-07: 연구비 집행 데이터 시각화
9. UC-08: 학생 데이터 시각화

### Phase 4 - User Management & Utilities
10. UC-10: 사용자 프로필 관리
11. UC-11: 로그아웃
12. UC-12: 데이터 업로드 이력 조회

---

## Key Dependencies

### Technology Stack
- **Backend:** Django 4.x
- **Database:** PostgreSQL (Supabase)
- **Frontend:** Django Templates + Chart.js
- **Data Processing:** Pandas
- **Authentication:** Django Session Framework

### External Systems
- Supabase (PostgreSQL)
- Django Admin (for data upload)
- Chart.js (via CDN)

---

## Testing Strategy

### Unit Tests
- 각 validator 함수 테스트
- Parser 로직 테스트
- Aggregator 계산 로직 테스트

### Integration Tests
- 업로드 플로우 전체 테스트
- 인증/인가 플로우 테스트
- 데이터 조회 및 필터링 테스트

### E2E Tests
- 사용자 여정 기반 시나리오 테스트
- 각 use case의 happy path 테스트

### Performance Tests
- 대용량 데이터 업로드 테스트
- 동시 접속자 테스트
- 차트 렌더링 성능 테스트

---

## References

- [Product Requirements Document](../prd.md)
- [User Flow Documentation](../userflow.md)
- [Database Schema](../database.md)
- [Common Modules](../common-modules.md)
- [Technical Suggestions](../technical_suggestion.md)

---

## Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-02 | Claude Code | Initial summary covering all 12 use cases |

---

**Document Status:** Draft
**Last Updated:** 2025-11-02
**Total Use Cases:** 12
**Completed Detailed Specs:** 3 (UC-01, UC-02, UC-03)
**Summary Specs:** 9 (UC-04 ~ UC-12)
