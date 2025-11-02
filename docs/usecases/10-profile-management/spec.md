# Use Case Specification: 사용자 프로필 관리

## Use Case ID
UC-10

## Use Case Name
사용자 프로필 관리 (Profile Management)

## Quick Reference
**Detailed specification available in:** [Use Cases Summary](../SUMMARY.md#uc-10-사용자-프로필-관리-profile-management)

## Actor
**Primary Actor:** 로그인된 사용자

## Description
사용자가 본인의 프로필 정보(이름, 소속, 직책)를 수정하고 비밀번호를 변경하는 프로세스.

## Two Main Functions

### 1. 개인정보 수정
- 이름, 소속 부서, 직책 수정
- 입력값 검증
- 데이터베이스 업데이트

### 2. 비밀번호 변경
- 현재 비밀번호 확인
- 새 비밀번호 입력 및 검증
- 비밀번호 해싱 후 업데이트

## Read-only Fields
- 이메일 (변경 불가)
- role (관리자만 변경 가능)
- 가입일

## Business Rules
- 이메일 변경 불가
- role 변경 불가 (관리자만)
- 비밀번호 변경 시 현재 비밀번호 검증 필수
- 새 비밀번호가 현재와 동일 시 경고

## References
- **Detailed Flow:** [SUMMARY.md - UC-10](../SUMMARY.md#uc-10-사용자-프로필-관리-profile-management)
- **Userflow:** `/docs/userflow.md` - Section 10
- **Database:** `/docs/database.md` - users table

---

**For complete specification see:** [Use Cases Summary](../SUMMARY.md#uc-10-사용자-프로필-관리-profile-management)
