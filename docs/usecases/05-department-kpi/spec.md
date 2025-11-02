# Use Case Specification: 학과별 KPI 데이터 시각화

## Use Case ID
UC-05

## Use Case Name
학과별 KPI 데이터 시각화 조회 (Department KPI Visualization)

## Quick Reference
**Detailed specification available in:** [Use Cases Summary](../SUMMARY.md#uc-05-학과별-kpi-데이터-시각화-department-kpi-visualization)

## Actor
**Primary Actor:** 로그인된 사용자

## Description
사용자가 학과별 KPI 지표(취업률, 교원 수, 기술이전 수입액, 학술대회 개최 횟수)를 다양한 필터와 차트로 조회하고 분석하는 프로세스.

## Preconditions
- 사용자가 로그인되어 있다
- `department_kpi` 테이블에 데이터가 존재한다

## Main Flow
1. KPI 시각화 페이지 (`/analytics/department-kpi`) 접근
2. 필터 옵션 선택 (연도, 대학, 학과, KPI 지표)
3. 권한별 데이터 범위 제한 적용
4. 데이터 조회 및 집계
5. 통계 계산 (평균, 최고/최저, 증감률)
6. 시각화 차트 렌더링
7. 데이터 테이블 뷰 제공 (토글)

## Supported Filters
- 평가년도 (단일/범위)
- 단과대학
- 학과 (단일/복수)
- KPI 지표 (취업률, 전임교원 수, 초빙교원 수, 기술이전 수입액, 국제학술대회 개최 횟수)

## Chart Types
- 학과별 취업률 비교 (막대 그래프)
- 학과별 교원 현황 (누적 막대 그래프)
- 학과별 기술이전 수입액 (막대 그래프)
- 연도별 KPI 추이 (라인 차트)
- 단과대학별 KPI 비교 (그룹 막대 그래프)

## Key Features
- 차트 타입 전환 (막대 ↔ 라인)
- 데이터 내보내기 (CSV, Excel)
- 차트 이미지 저장
- 인터랙티브 툴팁

## References
- **Detailed Flow:** [SUMMARY.md - UC-05](../SUMMARY.md#uc-05-학과별-kpi-데이터-시각화-department-kpi-visualization)
- **Userflow:** `/docs/userflow.md` - Section 5
- **Database:** `/docs/database.md` - department_kpi table
- **Related Use Cases:** UC-04 (Dashboard), UC-06~08 (Other visualizations)

---

**For complete specification see:** [Use Cases Summary](../SUMMARY.md#uc-05-학과별-kpi-데이터-시각화-department-kpi-visualization)
