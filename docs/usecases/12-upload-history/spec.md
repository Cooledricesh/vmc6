# Use Case Specification: 데이터 업로드 이력 조회

## Use Case ID
UC-12

## Use Case Name
데이터 업로드 이력 조회 (Upload History View)

## Quick Reference
**Detailed specification available in:** [Use Cases Summary](../SUMMARY.md#uc-12-데이터-업로드-이력-조회-upload-history-view)

## Actor
**Primary Actor:** 로그인된 사용자

## Description
사용자가 과거에 업로드한 파일의 이력을 조회하고 상세 정보를 확인하는 프로세스.

## Preconditions
- 사용자가 로그인되어 있다
- `upload_history` 테이블에 데이터가 존재한다

## Main Flow
1. 데이터 히스토리 페이지 (`/data/history`) 접근
2. 필터 옵션 선택 (기간, 데이터 타입, 상태, 업로드자)
3. 권한별 데이터 범위 제한
   - 일반 사용자: 본인 이력만
   - 관리자: 전체 이력
4. 업로드 이력 조회
5. 이력 정보 집계 및 통계 계산
6. 목록 테이블 렌더링
7. 특정 이력 클릭 시 상세 정보 모달 표시

## Supported Filters
- 업로드 기간 (시작일, 종료일)
- 데이터 타입 (전체, KPI, 논문, 연구비, 학생)
- 업로드 상태 (전체, 성공, 실패)
- 업로드자 검색 (관리자만)

## Displayed Information
- 업로드 일시, 파일명, 데이터 타입
- 업로드자, 상태 (성공/실패)
- 저장된 행 수 (성공 시)
- 오류 메시지 (실패 시)

## Detail View Features
- **성공 시:** 데이터 미리보기, 시각화 페이지로 이동
- **실패 시:** 오류 메시지, 오류 로그 다운로드
- 동일 파일 재업로드 버튼

## References
- **Detailed Flow:** [SUMMARY.md - UC-12](../SUMMARY.md#uc-12-데이터-업로드-이력-조회-upload-history-view)
- **Userflow:** `/docs/userflow.md` - Section 12
- **Database:** `/docs/database.md` - upload_history table
- **Related Use Cases:** UC-03 (데이터 업로드)

---

**For complete specification see:** [Use Cases Summary](../SUMMARY.md#uc-12-데이터-업로드-이력-조회-upload-history-view)
