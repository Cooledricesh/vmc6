# Use Case Specification: 로그인

## Use Case ID
UC-02

## Use Case Name
사용자 로그인 (User Login)

## Actor
**Primary Actor:** 등록된 사용자 (admin, manager, viewer)

**Secondary Actor:**
- Django 세션 관리 시스템
- 데이터베이스

## Description
등록되고 승인된 사용자가 이메일과 비밀번호를 사용하여 시스템에 인증하고 대시보드에 접근하는 프로세스.

## Preconditions
- 사용자가 회원가입을 완료했다
- 사용자 계정이 관리자에 의해 승인되었다 (status = 'active')
- 사용자가 로그인 페이지(`/login`)에 접근할 수 있다

## Postconditions
**Success:**
- Django 세션이 생성된다
- 세션 쿠키가 클라이언트에 전달된다
- 사용자가 대시보드 페이지(`/dashboard`)로 리디렉션된다
- 로그인 시간이 기록된다 (선택적)

**Failure:**
- 세션이 생성되지 않는다
- 사용자는 로그인 페이지에 머물며 오류 메시지를 받는다

## Trigger
사용자가 다음 중 하나를 수행:
- **루트 페이지(`/`) 접근 (미인증 상태)**
- 로그인 페이지(`/login`) URL로 직접 접근
- 로그아웃 상태에서 인증 필요 페이지 접근 시 자동 리디렉션

---

## Main Flow (Happy Path)

### Step 0: 루트 페이지 접근 (선택적 진입점)
**Actor:** 사용자 (미인증)

**Action:**
- 사용자가 루트 URL(`/`) 접근
- 또는 도메인만 입력 (예: `university.edu`)

**System Response:**
```python
def index_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # AF-5로 분기
    return login_view(request)  # Step 1로 진행
```
- 세션 확인: `request.user.is_authenticated`
- **미인증 시**: 로그인 폼 렌더링 (Step 1로 진행)
- **인증됨 시**: 대시보드로 리디렉션 (AF-5)

### Step 1: 로그인 페이지 접근
**Actor:** 사용자
**Action:**
- 사용자가 로그인 페이지(`/login`) URL로 접근
- 또는 로그아웃 상태에서 인증 필요 페이지 접근 시 자동 리디렉션

**System Response:**
- 로그인 폼 렌더링 (이메일, 비밀번호 입력 필드)
- "비밀번호 찾기" 링크 표시
- "회원가입" 링크 표시

### Step 2: 인증 정보 입력
**Actor:** 사용자
**Action:**
- 이메일 주소 입력
- 비밀번호 입력

### Step 3: 로그인 버튼 클릭
**Actor:** 사용자
**Action:** "로그인" 버튼 클릭

### Step 4: 입력값 검증
**Actor:** 시스템
**Action:**
- 필수 항목 누락 여부 확인
  - 이메일 필드 비어있지 않은지 확인
  - 비밀번호 필드 비어있지 않은지 확인
- 이메일 형식 기본 검증

**System Response:**
- 검증 통과 시 다음 단계 진행

### Step 5: 사용자 인증
**Actor:** 시스템
**Action:**
```python
# 이메일로 사용자 조회
try:
    user = User.objects.get(email=email)
except User.DoesNotExist:
    # 사용자 없음 (보안상 구체적 오류 노출 안 함)
    return authentication_failed()

# 비밀번호 검증
if not check_password(password, user.password):
    # 비밀번호 불일치
    return authentication_failed()
```

**System Response:**
- 인증 성공: 다음 단계 진행
- 인증 실패: AF-1 (인증 실패) 플로우

### Step 6: 사용자 상태 확인
**Actor:** 시스템
**Action:**
```python
if user.status == 'pending':
    return approval_pending_response()
elif user.status == 'inactive':
    return account_inactive_response()
elif user.status == 'active':
    # 정상 로그인 진행
    pass
```

**System Response:**
- status = 'active': 다음 단계 진행
- status = 'pending': AF-2 (승인 대기) 플로우
- status = 'inactive': AF-3 (계정 비활성화) 플로우

### Step 7: 세션 생성
**Actor:** 시스템
**Action:**
```python
# Django 세션 생성
from django.contrib.auth import login

login(request, user)
# 세션에 저장되는 정보:
# - user.id
# - user.email
# - user.role
# - user.department

# 선택적: 로그인 시간 기록
user.last_login = timezone.now()
user.save(update_fields=['last_login'])
```

**Database Changes:**
- Django session framework가 `django_session` 테이블에 세션 레코드 생성
- `users.last_login` 업데이트 (선택적)

**System Response:**
- 세션 쿠키 생성 (sessionid)
- HTTP 응답 헤더에 Set-Cookie 포함

### Step 8: 대시보드 리디렉션
**Actor:** 시스템
**System Response:**
- HTTP 302 리디렉션: `/dashboard`
- 브라우저가 세션 쿠키와 함께 대시보드 페이지 요청
- 대시보드 페이지 렌더링

---

## Alternative Flows

### AF-1: 인증 실패 (이메일 또는 비밀번호 오류)
**Trigger:** Step 5에서 이메일 미존재 또는 비밀번호 불일치

**Flow:**
1. 시스템이 인증 실패 처리
2. 일반적인 오류 메시지 표시 (보안 강화)
   - "이메일 또는 비밀번호가 올바르지 않습니다"
   - (어느 것이 틀렸는지 명시하지 않음)
3. 입력한 이메일 주소 유지
4. 비밀번호 필드 초기화
5. 로그인 페이지 유지
6. 실패 횟수 카운트 증가 (선택적, 계정 잠금 정책용)

**Return:** Step 2 (사용자가 재입력)

### AF-2: 승인 대기 상태
**Trigger:** Step 6에서 user.status = 'pending'

**Flow:**
1. 시스템이 승인 대기 상태 감지
2. 모달 또는 알림 메시지 표시
   ```
   계정 승인 대기 중

   관리자 승인이 완료되면 로그인할 수 있습니다.
   승인 관련 문의는 관리자에게 연락 바랍니다.
   ```
3. 로그인 페이지 유지
4. 세션 생성하지 않음

**Return:** Step 1 (로그인 페이지)

### AF-3: 계정 비활성화
**Trigger:** Step 6에서 user.status = 'inactive'

**Flow:**
1. 시스템이 비활성화 상태 감지
2. 알림 메시지 표시
   ```
   계정이 비활성화되었습니다

   이 계정은 현재 사용할 수 없습니다.
   자세한 내용은 관리자에게 문의하시기 바랍니다.

   관리자 이메일: admin@university.ac.kr
   ```
3. 로그인 페이지 유지
4. 세션 생성하지 않음

**Return:** Step 1

### AF-4: 필수 항목 누락
**Trigger:** Step 4에서 이메일 또는 비밀번호 비어있음

**Flow:**
1. 시스템이 필수 항목 누락 감지
2. 각 필드 하단에 오류 메시지 표시
   - 이메일 비어있음: "이메일을 입력해주세요"
   - 비밀번호 비어있음: "비밀번호를 입력해주세요"
3. 입력한 값 유지
4. 포커스를 첫 번째 오류 필드로 이동

**Return:** Step 3 (사용자가 입력 완료 후 재시도)

### AF-5: 이미 로그인된 상태
**Trigger:** Step 1에서 유효한 세션이 이미 존재함

**Flow:**
1. 시스템이 현재 세션 확인
   ```python
   if request.user.is_authenticated:
       return redirect('/dashboard')
   ```
2. 즉시 대시보드 페이지로 리디렉션
3. 로그인 폼 표시하지 않음

**Return:** Exit to `/dashboard`

---

## Exception Flows

### EF-1: 데이터베이스 연결 실패
**Trigger:** Step 5에서 데이터베이스 연결 불가

**Flow:**
1. 시스템이 `DatabaseError` 예외 감지
2. 에러 로그 기록
3. 사용자에게 오류 메시지 표시
   - "일시적인 시스템 오류가 발생했습니다. 잠시 후 다시 시도해주세요"
4. 입력 값 유지
5. 관리자에게 알림 (선택적)

**Return:** Step 3 (사용자가 재시도)

### EF-2: 세션 생성 실패
**Trigger:** Step 7에서 세션 저장소 오류

**Flow:**
1. 시스템이 세션 생성 실패 감지
2. 에러 로그 기록
3. 사용자에게 오류 메시지 표시
   - "로그인 처리 중 오류가 발생했습니다. 다시 시도해주세요"
4. 인증은 성공했지만 세션 미생성
5. 사용자가 재로그인 필요

**Return:** Step 1

### EF-3: 연속 로그인 실패
**Trigger:** 동일 계정으로 5회 이상 연속 실패 (선택적 기능)

**Flow:**
1. 시스템이 실패 횟수 임계값 초과 감지
2. 계정 임시 잠금 (15분)
3. 알림 메시지 표시
   ```
   로그인 시도 횟수 초과

   보안을 위해 계정이 일시적으로 잠겼습니다.
   15분 후 다시 시도하거나 비밀번호 찾기를 이용하세요.
   ```
4. 비밀번호 찾기 링크 제공
5. 로그 기록 및 관리자 알림

**Return:** Step 1 (15분 후)

### EF-4: CSRF 토큰 검증 실패
**Trigger:** POST 요청에 유효한 CSRF 토큰이 없음

**Flow:**
1. Django의 CSRF 미들웨어가 요청 차단
2. 403 Forbidden 응답
3. CSRF 오류 페이지 표시
   - "보안 토큰이 유효하지 않습니다. 페이지를 새로고침하고 다시 시도해주세요"
4. 새로고침 버튼 제공

**Return:** Step 1 (페이지 새로고침)

---

## Business Rules

### BR-1: 인증 방식
- MVP 단계: Django 세션 기반 인증
- 2단계 로드맵: JWT 토큰 기반 인증으로 전환 예정

### BR-2: 세션 유효 기간
- 기본 세션 타임아웃: 2주 (Django 설정)
- 브라우저 닫을 때 세션 유지 (쿠키 persistent)

### BR-3: 로그인 가능 상태
- status = 'active'인 사용자만 로그인 가능
- 'pending' 또는 'inactive' 상태는 로그인 불가

### BR-4: 보안 정책
- 비밀번호는 해싱되어 저장 (PBKDF2)
- 로그인 실패 시 구체적인 오류 정보 노출 금지
  - "이메일이 없습니다" (X)
  - "비밀번호가 틀렸습니다" (X)
  - "이메일 또는 비밀번호가 올바르지 않습니다" (O)

### BR-5: 계정 잠금 (선택적)
- 5회 연속 실패 시 15분 잠금
- 잠금 해제: 시간 경과 또는 비밀번호 재설정

---

## Non-functional Requirements

### NFR-1: 성능
- 로그인 처리 시간: 1초 이내
- 세션 조회 성능: 50ms 이내

### NFR-2: 보안
- HTTPS 통신 필수
- 비밀번호 평문 전송 방지
- CSRF 보호
- XSS 방지
- 세션 고정 공격 방지 (Django 자동 처리)

### NFR-3: 사용성
- 로그인 실패 시 이메일 주소 유지
- 명확한 오류 메시지 제공
- 접근성: 키보드 내비게이션 지원

### NFR-4: 신뢰성
- 세션 서버 장애 시 대체 수단 (Redis 클러스터)
- 로그인 실패 로그 기록

---

## Test Scenarios

### TS-1: 정상 로그인 (Happy Path)
**Given:**
- 승인된 사용자 계정 존재
  - 이메일: test@university.ac.kr
  - 비밀번호: test1234
  - status: active

**When:**
- 로그인 페이지 접근
- 이메일 입력: test@university.ac.kr
- 비밀번호 입력: test1234
- "로그인" 버튼 클릭

**Then:**
- 대시보드 페이지(`/dashboard`)로 리디렉션
- 세션 쿠키 설정
- 네비게이션 바에 사용자 이름 표시

### TS-2: 잘못된 이메일
**When:**
- 이메일: nonexistent@university.ac.kr (존재하지 않음)
- 비밀번호: test1234

**Then:**
- "이메일 또는 비밀번호가 올바르지 않습니다" 메시지
- 로그인 페이지 유지
- 입력한 이메일 유지
- 비밀번호 필드 초기화

### TS-3: 잘못된 비밀번호
**When:**
- 이메일: test@university.ac.kr (존재함)
- 비밀번호: wrongpassword

**Then:**
- "이메일 또는 비밀번호가 올바르지 않습니다" 메시지
- 로그인 페이지 유지
- 이메일 유지, 비밀번호 초기화

### TS-4: 승인 대기 계정
**Given:**
- 사용자 계정 존재
- status: pending

**When:**
- 올바른 이메일과 비밀번호 입력
- 로그인 시도

**Then:**
- "관리자 승인이 완료되면 로그인할 수 있습니다" 메시지
- 로그인 페이지 유지
- 세션 생성되지 않음

### TS-5: 비활성화 계정
**Given:**
- status: inactive

**When:**
- 올바른 이메일과 비밀번호 입력

**Then:**
- "계정이 비활성화되었습니다" 메시지
- 관리자 문의 안내
- 세션 생성되지 않음

### TS-6: 필수 항목 누락
**When:**
- 이메일만 입력, 비밀번호 비워둠
- 로그인 버튼 클릭

**Then:**
- "비밀번호를 입력해주세요" 메시지
- 입력한 이메일 유지

### TS-7: 이미 로그인된 상태
**Given:**
- 유효한 세션 존재

**When:**
- 로그인 페이지 URL 직접 접근

**Then:**
- 즉시 대시보드로 리디렉션
- 로그인 폼 표시하지 않음

### TS-8: 만료된 세션으로 보호된 페이지 접근
**Given:**
- 세션이 만료됨

**When:**
- `/dashboard` URL 접근

**Then:**
- 로그인 페이지로 리디렉션
- 쿼리 파라미터에 원래 URL 포함: `/login?next=/dashboard`
- 로그인 성공 후 원래 페이지로 리디렉션

### TS-9: SQL Injection 시도
**When:**
- 이메일: `admin' OR '1'='1' --`
- 비밀번호: anything

**Then:**
- Django ORM의 파라미터화된 쿼리로 방어
- "이메일 또는 비밀번호가 올바르지 않습니다" 메시지
- 정상적인 인증 실패 처리

### TS-10: XSS 시도
**When:**
- 이메일: `<script>alert('XSS')</script>`

**Then:**
- 이메일 형식 검증 실패 또는
- 정상 처리 후 템플릿 자동 이스케이프

---

## UI/UX Specifications

### Login Form
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         로그인
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

이메일
[                              ]

비밀번호
[                              ]

[       로그인       ]

[비밀번호 찾기] | [회원가입]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Error Display
```
이메일
[test@university.ac.kr        ]

비밀번호
[••••••••                      ]

⚠ 이메일 또는 비밀번호가 올바르지 않습니다

[       로그인       ]
```

### Pending Status Modal
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏳ 계정 승인 대기 중

관리자 승인이 완료되면 로그인할 수 있습니다.
승인 관련 문의는 관리자에게 연락 바랍니다.

          [  확인  ]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Related Use Cases
- **UC-01:** 회원가입
- **UC-04:** 대시보드 조회
- **UC-09:** 관리자 - 사용자 승인/거부
- **UC-11:** 로그아웃

## Dependencies
- Django Authentication Framework
- Django Session Framework
- PostgreSQL (Supabase)

## References
- `/docs/userflow.md` - Section 2
- `/docs/database.md` - users table
- `/docs/prd.md` - Section 6.1.1

## Change History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-02 | Claude Code | Initial creation based on userflow.md |

---

**Document Status:** Draft
**Last Updated:** 2025-11-02
**Reviewed By:** -
**Approved By:** -
