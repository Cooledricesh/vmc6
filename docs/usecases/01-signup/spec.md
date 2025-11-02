# Use Case Specification: 회원가입

## Use Case ID
UC-01

## Use Case Name
사용자 회원가입 (User Registration)

## Actor
**Primary Actor:** 신규 사용자 (모든 역할 예비 사용자)

**Secondary Actor:**
- 시스템 (데이터 검증 및 저장)
- 관리자 (가입 승인 담당자)

## Description
신규 사용자가 대시보드 시스템에 접근하기 위해 계정을 생성하는 프로세스. 사용자는 필수 정보를 입력하고, 시스템은 입력값을 검증한 후 승인 대기 상태로 계정을 생성한다.

## Preconditions
- 사용자는 회원가입 페이지(`/signup`)에 접근할 수 있다
- 사용자는 유효한 이메일 주소를 가지고 있다
- 시스템 데이터베이스가 정상 작동 중이다

## Postconditions
**Success:**
- 사용자 정보가 데이터베이스에 저장된다
- 사용자 상태가 'pending'으로 설정된다
- 사용자에게 관리자 승인 대기 안내가 표시된다
- 사용자는 로그인 페이지로 리디렉션된다

**Failure:**
- 사용자 정보가 데이터베이스에 저장되지 않는다
- 오류 메시지가 표시되고 입력 폼이 유지된다

## Trigger
사용자가 회원가입 페이지에서 "회원가입" 버튼을 클릭

---

## Main Flow (Happy Path)

### Step 1: 회원가입 페이지 접근
**Actor:** 사용자
**Action:**
- 사용자가 로그인 페이지 또는 메인 페이지에서 "회원가입" 링크를 클릭
- 시스템이 회원가입 페이지(`/signup`)를 표시

**System Response:**
- 회원가입 폼 렌더링 (이름, 이메일, 비밀번호, 비밀번호 확인, 소속 부서, 직책 입력 필드)

### Step 2: 사용자 정보 입력
**Actor:** 사용자
**Action:**
- 이름 입력 (필수)
- 이메일 입력 (필수)
- 비밀번호 입력 (필수, 최소 4자)
- 비밀번호 확인 입력 (필수)
- 소속 부서 입력 (선택)
- 직책 입력 (선택)

### Step 3: 회원가입 버튼 클릭
**Actor:** 사용자
**Action:** "회원가입" 버튼 클릭

### Step 4: 입력값 검증
**Actor:** 시스템
**Action:**
- 필수 항목 누락 여부 확인
  - 이름, 이메일, 비밀번호, 비밀번호 확인 필드 검증
- 이메일 형식 유효성 검사 (RFC 5322 표준)
- 비밀번호 정책 검증
  - 최소 4자 이상
- 비밀번호 일치 여부 확인

**System Response:**
- 모든 검증 통과 시 다음 단계 진행

### Step 5: 중복 검사
**Actor:** 시스템
**Action:**
- 입력된 이메일로 `users` 테이블 조회
- 이메일 중복 여부 확인

**System Response:**
- 중복되지 않음: 다음 단계 진행

### Step 6: 데이터 저장
**Actor:** 시스템
**Action:**
```python
# 비밀번호 해싱
hashed_password = make_password(password)

# 사용자 정보 저장
user = User.objects.create(
    email=email,
    password=hashed_password,
    name=name,
    department=department,
    position=position,
    role='viewer',  # 기본 역할
    status='pending'  # 승인 대기
)
```

**Database Changes:**
- `users` 테이블에 새 레코드 INSERT
- `created_at` 자동 설정 (현재 시각)
- `updated_at` 자동 설정 (현재 시각)

### Step 7: 성공 응답
**Actor:** 시스템
**System Response:**
- 성공 팝업 메시지 표시:
  ```
  회원가입이 완료되었습니다.
  관리자 승인 후 로그인할 수 있습니다.
  ```
- 팝업 확인 버튼 클릭 시 로그인 페이지(`/login`)로 리디렉션

---

## Alternative Flows

### AF-1: 필수 항목 누락
**Trigger:** Step 4에서 필수 항목이 비어있음

**Flow:**
1. 시스템이 누락된 필드 식별
2. 각 누락된 필드 하단에 오류 메시지 표시
   - "이름을 입력해주세요"
   - "이메일을 입력해주세요"
   - "비밀번호를 입력해주세요"
3. 입력한 데이터 유지 (비밀번호 제외)
4. 포커스를 첫 번째 오류 필드로 이동
5. 사용자가 수정 후 재시도

**Return:** Step 3 (회원가입 버튼 클릭)

### AF-2: 이메일 형식 오류
**Trigger:** Step 4에서 이메일 형식이 유효하지 않음

**Flow:**
1. 시스템이 이메일 형식 검증 실패 감지
2. 이메일 필드 하단에 오류 메시지 표시
   - "유효한 이메일 주소를 입력해주세요"
3. 이메일 필드 강조 (빨간색 테두리)
4. 기존 입력값 유지
5. 사용자가 수정 후 재시도

**Return:** Step 3

### AF-3: 비밀번호 정책 위반
**Trigger:** Step 4에서 비밀번호가 최소 4자 미만

**Flow:**
1. 시스템이 비밀번호 길이 검증 실패 감지
2. 비밀번호 필드 하단에 오류 메시지 표시
   - "비밀번호는 최소 4자 이상이어야 합니다"
3. 비밀번호 필드 강조
4. 비밀번호 및 비밀번호 확인 필드 초기화
5. 사용자가 재입력

**Return:** Step 3

### AF-4: 비밀번호 불일치
**Trigger:** Step 4에서 비밀번호와 비밀번호 확인 값이 다름

**Flow:**
1. 시스템이 비밀번호 불일치 감지
2. 비밀번호 확인 필드 하단에 오류 메시지 표시
   - "비밀번호가 일치하지 않습니다"
3. 비밀번호 확인 필드 강조
4. 비밀번호 확인 필드만 초기화
5. 사용자가 재입력

**Return:** Step 3

### AF-5: 이메일 중복
**Trigger:** Step 5에서 이미 등록된 이메일 검출

**Flow:**
1. 시스템이 데이터베이스에서 중복 이메일 발견
2. 이메일 필드 하단에 오류 메시지 표시
   - "이미 등록된 이메일입니다"
3. 추가 안내 메시지 표시
   - "이미 계정이 있으신가요? [로그인하기]"
   - "비밀번호를 잊으셨나요? [비밀번호 찾기]"
4. 프로세스 중단
5. 사용자가 다른 이메일로 재시도 또는 로그인 페이지로 이동

**Return:** Step 3 또는 Exit to `/login`

---

## Exception Flows

### EF-1: 데이터베이스 연결 실패
**Trigger:** Step 5 또는 Step 6에서 데이터베이스 연결 불가

**Flow:**
1. 시스템이 `DatabaseError` 예외 감지
2. 에러 로그 기록
   ```python
   logger.error(f"Database connection failed during signup: {str(e)}")
   ```
3. 사용자에게 일반적인 오류 메시지 표시
   - "시스템 오류가 발생했습니다. 잠시 후 다시 시도해주세요"
4. 입력한 데이터 유지 (비밀번호 제외)
5. 관리자에게 알림 (선택적)

**Return:** Step 3 (사용자가 재시도)

### EF-2: 트랜잭션 실패
**Trigger:** Step 6에서 데이터 저장 중 오류 발생

**Flow:**
1. 시스템이 `IntegrityError` 또는 기타 DB 예외 감지
2. 트랜잭션 자동 롤백 (Django default)
3. 에러 로그 기록
4. 사용자에게 오류 메시지 표시
   - "회원가입 처리 중 오류가 발생했습니다. 다시 시도해주세요"
5. 입력 폼 유지

**Return:** Step 3

### EF-3: 네트워크 타임아웃
**Trigger:** 클라이언트와 서버 간 통신 타임아웃

**Flow:**
1. 클라이언트가 타임아웃 감지 (30초)
2. 사용자에게 타임아웃 메시지 표시
   - "요청 시간이 초과되었습니다. 다시 시도해주세요"
3. 서버 측에서 이메일 기반 중복 체크로 재가입 방지
4. 사용자가 재시도 시 AF-5 (이메일 중복) 플로우로 분기 가능

**Return:** Step 3

### EF-4: SQL Injection 시도
**Trigger:** 악의적인 SQL 코드가 입력값에 포함됨

**Flow:**
1. Django ORM의 파라미터화된 쿼리로 자동 방어
2. 입력값 이스케이프 처리
3. 정상 플로우 진행 (추가 처리 불필요)
4. 보안 로그 기록 (선택적)

**Return:** Normal flow continues

---

## Business Rules

### BR-1: 이메일 유일성
- 각 이메일 주소는 시스템 내에서 유일해야 함
- `users.email` 컬럼에 UNIQUE 제약 조건 적용

### BR-2: 비밀번호 정책
- 최소 길이: 4자 (MVP 기준, 향후 강화 예정)
- 해싱 알고리즘: Django의 `make_password()` (PBKDF2)
- 평문 저장 금지

### BR-3: 기본 역할 할당
- 신규 가입 시 기본 역할: `viewer`
- 역할 변경은 관리자만 가능

### BR-4: 승인 프로세스
- 신규 가입 시 상태: `pending` (승인 대기)
- `pending` 상태에서는 로그인 불가
- 관리자 승인 후 `active` 상태로 변경 시 로그인 가능

### BR-5: 필수 입력 항목
- 이름 (name)
- 이메일 (email)
- 비밀번호 (password)
- 비밀번호 확인

### BR-6: 선택 입력 항목
- 소속 부서 (department)
- 직책 (position)

---

## Non-functional Requirements

### NFR-1: 성능
- 회원가입 처리 시간: 3초 이내
- 중복 이메일 체크 쿼리: 100ms 이내 (`email` 인덱스 활용)

### NFR-2: 보안
- 비밀번호 해싱 처리 (PBKDF2-SHA256)
- HTTPS 통신 필수
- CSRF 토큰 검증 (Django 기본 미들웨어)
- XSS 방지 (템플릿 자동 이스케이프)

### NFR-3: 사용성
- 오류 메시지는 구체적이고 실행 가능해야 함
- 입력 검증 실패 시 기존 입력값 유지 (비밀번호 제외)
- 모바일 반응형 디자인 지원

### NFR-4: 접근성
- 키보드 내비게이션 지원
- 스크린 리더 호환 (ARIA 레이블)
- 충분한 색상 대비 (WCAG 2.1 AA 기준)

### NFR-5: 신뢰성
- 동시 가입 요청 처리 (데이터베이스 UNIQUE 제약으로 보장)
- 트랜잭션 보장 (원자성)

---

## Test Scenarios

### TS-1: 정상 회원가입 (Happy Path)
**Given:**
- 회원가입 페이지에 접근
- 유효한 이메일 주소 준비

**When:**
- 모든 필수 정보 입력
  - 이름: "홍길동"
  - 이메일: "hong@university.ac.kr"
  - 비밀번호: "test1234"
  - 비밀번호 확인: "test1234"
  - 소속 부서: "컴퓨터공학과"
  - 직책: "교수"
- "회원가입" 버튼 클릭

**Then:**
- 성공 메시지 표시
- 로그인 페이지로 리디렉션
- 데이터베이스에 사용자 레코드 생성
- status = 'pending'
- role = 'viewer'

### TS-2: 필수 항목 누락
**Given:** 회원가입 페이지

**When:**
- 이메일만 입력
- 다른 필수 항목 비워둠
- "회원가입" 버튼 클릭

**Then:**
- 이름 필드 오류: "이름을 입력해주세요"
- 비밀번호 필드 오류: "비밀번호를 입력해주세요"
- 비밀번호 확인 필드 오류: "비밀번호 확인을 입력해주세요"
- 입력한 이메일 유지
- 페이지 유지

### TS-3: 이메일 형식 오류
**Test Data:**
- "invalid-email"
- "test@"
- "@university.ac.kr"
- "test..user@university.ac.kr"

**Then:**
- "유효한 이메일 주소를 입력해주세요" 메시지 표시
- 이메일 필드 강조

### TS-4: 비밀번호 길이 부족
**When:**
- 비밀번호: "abc" (3자)
- 비밀번호 확인: "abc"

**Then:**
- "비밀번호는 최소 4자 이상이어야 합니다" 메시지 표시
- 비밀번호 필드 초기화

### TS-5: 비밀번호 불일치
**When:**
- 비밀번호: "test1234"
- 비밀번호 확인: "test4321"

**Then:**
- "비밀번호가 일치하지 않습니다" 메시지 표시
- 비밀번호 확인 필드 강조

### TS-6: 이메일 중복
**Given:**
- 기존 사용자: hong@university.ac.kr

**When:**
- 동일한 이메일로 회원가입 시도

**Then:**
- "이미 등록된 이메일입니다" 메시지 표시
- 로그인 페이지 링크 제공
- 비밀번호 찾기 링크 제공

### TS-7: 특수문자 포함 이름
**When:**
- 이름: "이서연·정현우" (중점 포함)

**Then:**
- 허용 가능한 특수문자 범위 내에서 정상 처리
- 또는 "이름에 허용되지 않는 문자가 포함되어 있습니다" 오류

### TS-8: 최대 길이 초과
**When:**
- 이름: 51자 이상 입력
- 소속 부서: 101자 이상 입력

**Then:**
- "이름은 최대 50자까지 입력 가능합니다" 오류 메시지
- "소속 부서는 최대 100자까지 입력 가능합니다" 오류 메시지

### TS-9: 동시 가입 요청 (Race Condition)
**Given:**
- 동일한 이메일로 2개의 가입 요청이 거의 동시에 발생

**When:**
- 두 요청이 중복 검사를 통과하고 동시에 INSERT 시도

**Then:**
- 데이터베이스 UNIQUE 제약으로 하나만 성공
- 나중 요청은 `IntegrityError` 발생
- 사용자에게 "이미 등록된 이메일입니다" 메시지 표시

### TS-10: XSS 공격 시도
**When:**
- 이름: `<script>alert('XSS')</script>`
- 소속 부서: `<img src=x onerror=alert('XSS')>`

**Then:**
- Django 템플릿 자동 이스케이프로 방어
- 데이터베이스 저장: 원본 문자열 그대로
- 화면 표시: HTML 엔티티로 이스케이프 (`&lt;script&gt;...`)

---

## UI/UX Specifications

### Form Layout
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         회원가입
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

이름 *
[                              ]

이메일 *
[                              ]

비밀번호 *
[                              ]

비밀번호 확인 *
[                              ]

소속 부서
[                              ]

직책
[                              ]

[      회원가입      ]

이미 계정이 있으신가요? [로그인]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Error Display
```
이메일 *
[hong@university.ac.kr        ]
⚠ 이미 등록된 이메일입니다

비밀번호 *
[••••                          ]
⚠ 비밀번호는 최소 4자 이상이어야 합니다
```

### Success Message (Modal)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ 회원가입 완료

회원가입이 완료되었습니다.
관리자 승인 후 로그인할 수 있습니다.

          [  확인  ]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Related Use Cases
- **UC-02:** 로그인
- **UC-09:** 관리자 - 사용자 승인/거부

## Dependencies
- Django Authentication Framework
- PostgreSQL (Supabase)
- Email validation library

## References
- `/docs/userflow.md` - Section 1
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
