# Use Case Specification: 관리자 - 사용자 승인/거부

## Use Case ID
UC-09

## Use Case Name
관리자 - 사용자 승인/거부 (User Approval Management)

## Quick Reference
**Detailed specification available in:** [Use Cases Summary](../SUMMARY.md#uc-09-관리자---사용자-승인거부-user-approval-management)

## Actor
**Primary Actor:** 관리자 (admin role)

## Description
관리자가 회원가입 신청한 사용자를 승인하거나 거부하여 계정 활성화를 관리하는 프로세스.

## Preconditions
- 관리자 권한 (admin role)
- Django Admin 접근 권한

## Main Flow
1. Django Admin 페이지 (`/admin`) 접근
2. 사용자 목록 탭 선택
3. 필터 적용 (기본: pending 상태)
4. 특정 사용자 선택
5. **승인:** status → 'active', 승인자 기록
6. **거부:** status → 'inactive', 거부 사유 입력 및 기록
7. 데이터베이스 업데이트
8. 관리 로그 기록
9. 사용자 목록 갱신

## Business Rules
- admin role만 승인/거부 가능
- 거부 시 거부 사유 필수
- 승인자/거부자 추적
- 자기 자신 승인/거부 불가

## Status Transitions
- pending → active (승인)
- pending → inactive (거부)

## References
- **Detailed Flow:** [SUMMARY.md - UC-09](../SUMMARY.md#uc-09-관리자---사용자-승인거부-user-approval-management)
- **Userflow:** `/docs/userflow.md` - Section 9
- **Database:** `/docs/database.md` - users table
- **Related Use Cases:** UC-01 (회원가입)

---

**For complete specification see:** [Use Cases Summary](../SUMMARY.md#uc-09-관리자---사용자-승인거부-user-approval-management)
