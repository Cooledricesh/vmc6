# Use Case Specification: 논문 게재 데이터 시각화

## Use Case ID
UC-06

## Use Case Name
논문 게재 데이터 시각화 조회 (Publications Visualization)

## Quick Reference
**Detailed specification available in:** [Use Cases Summary](../SUMMARY.md#uc-06-논문-게재-데이터-시각화-publications-visualization)

## Actor
**Primary Actor:** 로그인된 사용자

## Description
사용자가 논문 게재 데이터(저널 등급, Impact Factor, 과제연계 등)를 다양한 필터와 차트로 조회하고 분석하는 프로세스.

## Supported Filters
- 게재일 기간
- 단과대학/학과
- 저널 등급 (SCIE, KCI, SCOPUS, etc.)
- 주저자명 검색
- 과제연계여부

## Chart Types
- 학과별 논문 게재 수 (막대)
- 연도별 논문 추이 (라인)
- 저널 등급별 분포 (파이)
- 주저자별 게재 현황 (막대, 상위 10명)
- 과제연계 vs 비연계 (파이)
- Impact Factor 분포 (히스토그램/박스 플롯)

## Key Statistics
- 총 논문 수
- 평균 Impact Factor (SCIE 논문)
- 과제연계 비율
- 최다 게재 학과

## References
- **Detailed Flow:** [SUMMARY.md - UC-06](../SUMMARY.md#uc-06-논문-게재-데이터-시각화-publications-visualization)
- **Userflow:** `/docs/userflow.md` - Section 6
- **Database:** `/docs/database.md` - publications table

---

**For complete specification see:** [Use Cases Summary](../SUMMARY.md#uc-06-논문-게재-데이터-시각화-publications-visualization)
