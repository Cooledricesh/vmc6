# Use Case Specification: 연구비 집행 데이터 시각화

## Use Case ID
UC-07

## Use Case Name
연구비 집행 데이터 시각화 조회 (Research Budget Visualization)

## Quick Reference
**Detailed specification available in:** [Use Cases Summary](../SUMMARY.md#uc-07-연구비-집행-데이터-시각화-research-budget-visualization)

## Actor
**Primary Actor:** 로그인된 사용자

## Description
사용자가 연구비 집행 데이터(총연구비, 집행금액, 집행률, 집행항목 등)를 다양한 필터와 차트로 조회하고 분석하는 프로세스.

## Data Model
- `research_projects`: 과제 기본 정보
- `execution_records`: 상세 집행 내역
- `v_project_execution_rate`: 집행률 계산 뷰

## Supported Filters
- 집행일자 기간
- 소속학과
- 지원기관
- 연구책임자명 검색
- 집행항목
- 집행상태

## Chart Types
- 학과별 연구비 수주 현황 (막대)
- 지원기관별 연구비 분포 (파이/도넛)
- 집행항목별 지출 현황 (막대)
- 연도별 연구비 추이 (듀얼 축 라인)
- 연구책임자별 연구비 현황 (막대, 상위 10명)
- 과제별 집행률 (막대/히트맵)

## Key Statistics
- 총 연구비
- 총 집행금액
- 평균 집행률
- 과제 수

## References
- **Detailed Flow:** [SUMMARY.md - UC-07](../SUMMARY.md#uc-07-연구비-집행-데이터-시각화-research-budget-visualization)
- **Userflow:** `/docs/userflow.md` - Section 7
- **Database:** `/docs/database.md` - research_projects, execution_records tables

---

**For complete specification see:** [Use Cases Summary](../SUMMARY.md#uc-07-연구비-집행-데이터-시각화-research-budget-visualization)
