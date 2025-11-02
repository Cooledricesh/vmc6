# Use Case Specification: 로그아웃

## Use Case ID
UC-11

## Use Case Name
로그아웃 (Logout)

## Quick Reference
**Detailed specification available in:** [Use Cases Summary](../SUMMARY.md#uc-11-로그아웃-logout)

## Actor
**Primary Actor:** 로그인된 사용자

## Description
사용자가 시스템에서 로그아웃하여 세션을 종료하는 프로세스.

## Main Flow
1. 네비게이션 바의 사용자 메뉴 클릭
2. 로그아웃 버튼 클릭
3. 확인 팝업 (선택적)
4. Django 세션 종료
   - 세션 쿠키 삭제
   - 서버 측 세션 데이터 제거
5. 애플리케이션 전역 상태 초기화
6. 로그인 페이지로 리디렉션

## Session Cleanup
- 클라이언트 측: 세션 쿠키 (sessionid) 삭제
- 서버 측: Django session framework가 세션 invalidation
- 로그아웃 시간 기록 (선택적)

## Alternative Flows
- 이미 로그아웃 상태: 로그인 페이지로 리디렉션
- 여러 탭 동시 로그인: 한 탭 로그아웃 시 모든 탭 로그아웃

## References
- **Detailed Flow:** [SUMMARY.md - UC-11](../SUMMARY.md#uc-11-로그아웃-logout)
- **Userflow:** `/docs/userflow.md` - Section 11
- **Related Use Cases:** UC-02 (로그인)

---

**For complete specification see:** [Use Cases Summary](../SUMMARY.md#uc-11-로그아웃-logout)
