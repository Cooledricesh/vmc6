# Use Case Documentation

This directory contains detailed use case specifications for all 12 major user flows in the University Data Visualization Dashboard system.

## Use Case Index

| UC ID | Use Case Name | Status | Related Userflow Section |
|-------|---------------|--------|--------------------------|
| UC-01 | [회원가입](./01-signup/spec.md) | ✅ Complete | Section 1 |
| UC-02 | [로그인](./02-login/spec.md) | ✅ Complete | Section 2 |
| UC-03 | [엑셀 파일 업로드](./03-data-upload/spec.md) | ✅ Complete | Section 3 |
| UC-04 | [대시보드 조회](./04-dashboard/spec.md) | ✅ Complete | Section 4 |
| UC-05 | [학과별 KPI 데이터 시각화](./05-department-kpi/spec.md) | ✅ Complete | Section 5 |
| UC-06 | [논문 게재 데이터 시각화](./06-publications/spec.md) | ✅ Complete | Section 6 |
| UC-07 | [연구비 집행 데이터 시각화](./07-research-budget/spec.md) | ✅ Complete | Section 7 |
| UC-08 | [학생 데이터 시각화](./08-students/spec.md) | ✅ Complete | Section 8 |
| UC-09 | [관리자 - 사용자 승인/거부](./09-user-approval/spec.md) | ✅ Complete | Section 9 |
| UC-10 | [사용자 프로필 관리](./10-profile-management/spec.md) | ✅ Complete | Section 10 |
| UC-11 | [로그아웃](./11-logout/spec.md) | ✅ Complete | Section 11 |
| UC-12 | [데이터 업로드 이력 조회](./12-upload-history/spec.md) | ✅ Complete | Section 12 |

## Document Structure

Each use case specification follows a standardized format:

### Sections
1. **Basic Information**
   - Use Case ID, Name
   - Actors (Primary/Secondary)
   - Description
   - Preconditions/Postconditions
   - Trigger

2. **Flows**
   - Main Flow (Happy Path)
   - Alternative Flows
   - Exception Flows

3. **Rules & Requirements**
   - Business Rules
   - Non-functional Requirements

4. **Testing**
   - Test Scenarios

5. **Supporting Information**
   - UI/UX Specifications
   - Related Use Cases
   - Dependencies
   - References

## References
- [Product Requirements Document](../prd.md)
- [User Flow Documentation](../userflow.md)
- [Database Schema](../database.md)
- [Common Modules](../common-modules.md)

## Change History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | 2025-11-02 | Claude Code | Completed all UC-04 to UC-12 specifications |
| 1.0 | 2025-11-02 | Claude Code | Initial structure and UC-01 to UC-03 |

