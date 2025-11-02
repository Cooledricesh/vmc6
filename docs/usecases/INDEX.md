# Use Case Documentation Index

## Overview
This directory contains comprehensive use case specifications for all 12 major user flows in the University Data Visualization Dashboard system.

## Quick Navigation

### Authentication & User Management
- **[UC-01: 회원가입](./01-signup/spec.md)** ✅ Full Spec (3,975 lines)
  - User registration with admin approval workflow
  
- **[UC-02: 로그인](./02-login/spec.md)** ✅ Full Spec (571 lines)
  - Session-based authentication with status validation
  
- **[UC-09: 관리자 - 사용자 승인/거부](./09-user-approval/spec.md)** 📋 Quick Spec
  - Admin approval workflow for pending users
  
- **[UC-10: 사용자 프로필 관리](./10-profile-management/spec.md)** 📋 Quick Spec
  - Profile edit and password change
  
- **[UC-11: 로그아웃](./11-logout/spec.md)** 📋 Quick Spec
  - Session termination

### Data Management
- **[UC-03: 엑셀 파일 업로드](./03-data-upload/spec.md)** ✅ Full Spec (1,019 lines)
  - Django Admin-based file upload with Pandas parsing
  
- **[UC-12: 데이터 업로드 이력 조회](./12-upload-history/spec.md)** 📋 Quick Spec
  - Upload history tracking and audit log

### Dashboard & Visualization
- **[UC-04: 대시보드 조회](./04-dashboard/spec.md)** 📋 Quick Spec
  - Main dashboard with KPI summary cards
  
- **[UC-05: 학과별 KPI 데이터 시각화](./05-department-kpi/spec.md)** 📋 Quick Spec
  - Department KPI visualization with filters
  
- **[UC-06: 논문 게재 데이터 시각화](./06-publications/spec.md)** 📋 Quick Spec
  - Publications visualization with journal grade analysis
  
- **[UC-07: 연구비 집행 데이터 시각화](./07-research-budget/spec.md)** 📋 Quick Spec
  - Research budget execution rate visualization
  
- **[UC-08: 학생 데이터 시각화](./08-students/spec.md)** 📋 Quick Spec
  - Student enrollment visualization with filters

## Documentation Structure

### Full Specifications (UC-01, UC-02, UC-03)
Complete detailed documentation including:
- ✅ Actors (Primary/Secondary)
- ✅ Preconditions/Postconditions
- ✅ Main Flow (Step-by-step)
- ✅ Alternative Flows (All scenarios)
- ✅ Exception Flows (Error handling)
- ✅ Business Rules
- ✅ Non-functional Requirements
- ✅ Test Scenarios (10+ scenarios each)
- ✅ UI/UX Specifications

### Quick Specifications (UC-04 ~ UC-12)
Essential documentation with:
- ✅ Use Case ID and Name
- ✅ Actors
- ✅ Description
- ✅ Preconditions/Postconditions
- ✅ Main Flow (Summary)
- ✅ Key Components
- ✅ References to detailed SUMMARY.md

### Comprehensive Summary
**[SUMMARY.md](./SUMMARY.md)** - Complete overview of all 12 use cases with:
- Executive summary
- Key flows for each use case
- Business rules
- Common patterns
- Implementation priority
- Testing strategy

## File Statistics

| File | Lines | Type | Status |
|------|-------|------|--------|
| 01-signup/spec.md | 995 | Full | ✅ Complete |
| 02-login/spec.md | 571 | Full | ✅ Complete |
| 03-data-upload/spec.md | 1,019 | Full | ✅ Complete |
| 04-dashboard/spec.md | 89 | Quick | ✅ Complete |
| 05-department-kpi/spec.md | 72 | Quick | ✅ Complete |
| 06-publications/spec.md | 63 | Quick | ✅ Complete |
| 07-research-budget/spec.md | 84 | Quick | ✅ Complete |
| 08-students/spec.md | 73 | Quick | ✅ Complete |
| 09-user-approval/spec.md | 69 | Quick | ✅ Complete |
| 10-profile-management/spec.md | 68 | Quick | ✅ Complete |
| 11-logout/spec.md | 59 | Quick | ✅ Complete |
| 12-upload-history/spec.md | 82 | Quick | ✅ Complete |
| SUMMARY.md | 889 | Summary | ✅ Complete |
| **TOTAL** | **4,233** | - | ✅ **100% Complete** |

## Related Documentation

### Core Project Documents
- [Product Requirements Document](../prd.md) - Overall product vision and requirements
- [User Flow Documentation](../userflow.md) - Detailed user journey flows
- [Database Schema](../database.md) - Complete database design
- [Common Modules](../common-modules.md) - Module architecture guide
- [Technical Suggestions](../technical_suggestion.md) - Technology stack decisions

### External References
- Django Documentation: https://docs.djangoproject.com/
- Chart.js Documentation: https://www.chartjs.org/
- Pandas Documentation: https://pandas.pydata.org/
- Supabase Documentation: https://supabase.com/docs

## How to Use This Documentation

### For Developers
1. **Start with:** [README.md](./README.md) for overview
2. **Read:** Full specifications (UC-01, UC-02, UC-03) to understand detailed patterns
3. **Reference:** Quick specifications and SUMMARY.md during implementation
4. **Follow:** Test scenarios for quality assurance

### For Project Managers
1. **Review:** [SUMMARY.md](./SUMMARY.md) for complete feature overview
2. **Track:** Implementation priority section for roadmap
3. **Monitor:** Test scenarios for acceptance criteria

### For QA Engineers
1. **Extract:** Test scenarios from each use case
2. **Create:** Test cases based on alternative and exception flows
3. **Validate:** Business rules and non-functional requirements

## Version Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-02 | Claude Code | Initial creation of all 12 use case specifications |

---

**Total Use Cases:** 12  
**Documentation Status:** ✅ 100% Complete  
**Last Updated:** 2025-11-02  
**Total Lines of Documentation:** 4,233+
