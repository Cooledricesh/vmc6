# Use Case Specification: 학생 데이터 시각화

## Use Case ID
UC-08

## Use Case Name
학생 데이터 시각화 조회 (Students Visualization)

## Quick Reference
**Detailed specification available in:** [Use Cases Summary](../SUMMARY.md#uc-08-학생-데이터-시각화-students-visualization)

## Actor
**Primary Actor:** 로그인된 사용자

## Description
사용자가 학생 데이터(재학생 수, 학적상태, 과정구분 등)를 다양한 필터와 차트로 조회하고 분석하는 프로세스.

## Supported Filters
- 입학년도
- 단과대학/학과
- 학년 (0: 대학원, 1~4: 학부)
- 과정구분 (학사, 석사, 박사)
- 학적상태 (재학, 휴학, 졸업)
- 성별
- 지도교수명 검색

## Chart Types
- 학과별 재학생 수 (막대)
- 학년별 분포 (파이/도넛)
- 과정구분별 분포 (파이)
- 학적상태별 분포 (파이/막대)
- 입학년도별 학생 수 추이 (라인)
- 성별 분포 (파이)
- 지도교수별 지도 학생 수 (막대, 상위 10명)

## Key Statistics
- 총 학생 수
- 재학률
- 휴학률
- 남녀 비율

## References
- **Detailed Flow:** [SUMMARY.md - UC-08](../SUMMARY.md#uc-08-학생-데이터-시각화-students-visualization)
- **Userflow:** `/docs/userflow.md` - Section 8
- **Database:** `/docs/database.md` - students table

---

**For complete specification see:** [Use Cases Summary](../SUMMARY.md#uc-08-학생-데이터-시각화-students-visualization)
