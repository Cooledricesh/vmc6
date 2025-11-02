# Use Case Specification: 대시보드 조회

## Use Case ID
UC-04

## Use Case Name
대시보드 조회 (Dashboard View)

## Quick Reference
**Detailed specification available in:** [Use Cases Summary](../SUMMARY.md#uc-04-대시보드-조회-dashboard-view)

## Actor
**Primary Actor:** 로그인된 사용자 (모든 역할)

## Description
사용자가 시스템에 로그인한 후 전체 KPI 요약 정보와 주요 추이를 한눈에 파악할 수 있는 대시보드 페이지를 조회하는 프로세스.

## Preconditions
- 사용자가 로그인되어 있다
- 데이터가 업로드되어 있다 (선택적)

## Postconditions
**Success:**
- 대시보드 페이지가 렌더링된다
- 4개 KPI 요약 카드가 표시된다
- 주요 추이 그래프가 표시된다
- 최근 업데이트 정보가 표시된다

## Main Flow
1. 로그인된 사용자가 대시보드 페이지 (`/dashboard`) 접근
2. 시스템이 권한 및 소속 확인
3. 사용자 role에 따른 데이터 접근 범위 결정
4. 최근 데이터 조회 (기본: 최근 학기 또는 최근 연도)
5. KPI 계산 및 집계
6. 추이 데이터 계산 (최근 3개년, 전년 대비 증감률)
7. 최근 업데이트 정보 조회
8. 대시보드 렌더링

## Key Components
- **KPI 요약 카드 (4개)**
  1. 학과별 KPI (평균 취업률, 총 교원 수)
  2. 논문 수 (총합, 학과별, 등급별)
  3. 학생 수 (총합, 학과별, 학년별)
  4. 연구비 (총액, 총 집행액, 집행률)

- **주요 추이 그래프**
  - 연도별 라인 차트
  - 단과대학별 비교 막대 그래프

- **최근 업데이트 정보**
  - 각 데이터 타입별 마지막 업데이트 날짜 및 업로드자

## Data Access Rules
| Role | Access Level |
|------|--------------|
| admin | 전체 데이터 |
| manager | 전체 데이터 |
| viewer | 소속 부서 데이터만 |

## References
- **Detailed Flow:** [SUMMARY.md - UC-04](../SUMMARY.md#uc-04-대시보드-조회-dashboard-view)
- **Userflow:** `/docs/userflow.md` - Section 4
- **Database:** `/docs/database.md` - All tables
- **Related Use Cases:** UC-05~08 (Visualization pages)

---

**For complete specification including:**
- Alternative Flows
- Exception Flows
- Business Rules
- Test Scenarios
- UI/UX Specifications

**See:** [Use Cases Summary Document](../SUMMARY.md#uc-04-대시보드-조회-dashboard-view)
