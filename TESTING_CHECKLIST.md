# Testing Checklist: Python to JavaScript Serialization Fix

## 문제 해결 완료 ✓

모든 analytics views에서 chart 데이터를 `json.dumps()`로 감쌌습니다:

- ✓ `dashboard_view` - 3개 차트 데이터
- ✓ `department_kpi_view` - 2개 차트 데이터
- ✓ `publications_view` - 2개 차트 데이터
- ✓ `research_budget_view` - 2개 차트 데이터
- ✓ `students_view` - 2개 차트 데이터

## 수정된 파일

- `/Users/seunghyun/Test/vmc6/apps/analytics/views.py`

## 브라우저 테스트 체크리스트

서버가 실행 중인지 확인: http://127.0.0.1:8000/

### 1. 준비 단계

```bash
# 서버가 실행 중이 아니라면:
cd /Users/seunghyun/Test/vmc6
python manage.py runserver
```

### 2. 로그인

1. 브라우저에서 http://127.0.0.1:8000/login/ 접속
2. 테스트 계정으로 로그인:
   - Email: test_admin@example.com
   - Password: testpass123

### 3. 각 페이지 테스트

#### 3.1 Dashboard (http://127.0.0.1:8000/dashboard/)

**체크 항목:**
- [ ] 페이지가 정상적으로 로드됨
- [ ] 브라우저 콘솔에 JavaScript 에러가 없음 (F12 → Console 탭)
- [ ] 다음 에러가 **나타나지 않음**:
  - ❌ `The specified value "None" cannot be parsed`
  - ❌ `ReferenceError: False is not defined`
  - ❌ `ReferenceError: True is not defined`
  - ❌ `Unexpected token 'N'` (None 관련)

**테스트 방법:**
1. 페이지 로드 후 F12 눌러서 개발자 도구 열기
2. Console 탭에서 에러 메시지 확인
3. Elements/Inspector 탭에서 `<script>` 태그 내용 확인:
   ```javascript
   const employmentData = {"labels": [...], "datasets": [...]};  // ✓ 올바른 형식
   ```
   다음과 같은 형식이 **아니어야 함**:
   ```javascript
   const employmentData = {'labels': [...], 'data': [None, True, False]};  // ✗ 잘못된 형식
   ```

#### 3.2 Department KPI (http://127.0.0.1:8000/analytics/department-kpi/)

**체크 항목:**
- [ ] 페이지가 정상적으로 로드됨
- [ ] 콘솔에 JavaScript 에러 없음
- [ ] Chart 데이터에 `null`, `true`, `false` (소문자) 사용
- [ ] Python 리터럴 (`None`, `True`, `False`) 없음

#### 3.3 Publications (http://127.0.0.1:8000/analytics/publications/)

**체크 항목:**
- [ ] 페이지가 정상적으로 로드됨
- [ ] 콘솔에 JavaScript 에러 없음
- [ ] Pie chart 데이터가 올바른 JSON 형식

#### 3.4 Research Budget (http://127.0.0.1:8000/analytics/research-budget/)

**체크 항목:**
- [ ] 페이지가 정상적으로 로드됨
- [ ] 콘솔에 JavaScript 에러 없음
- [ ] Execution rate 데이터가 올바른 형식

#### 3.5 Students (http://127.0.0.1:8000/analytics/students/)

**체크 항목:**
- [ ] 페이지가 정상적으로 로드됨
- [ ] 콘솔에 JavaScript 에러 없음
- [ ] Enrollment 데이터가 올바른 형식

### 4. 추가 검증

#### 4.1 페이지 소스 확인

각 페이지에서:
1. 마우스 오른쪽 클릭 → "페이지 소스 보기"
2. `<script>` 태그를 찾아서 chart 데이터 확인
3. 다음 패턴이 보여야 함:
   ```javascript
   const chartData = {"labels":["CS","Math"],"datasets":[{"data":[85,null,90],"fill":false}]};
   ```

#### 4.2 Console에서 직접 확인

브라우저 콘솔 (F12 → Console)에서:
```javascript
// Chart 데이터 변수들이 정의되어 있는지 확인
console.log(typeof employmentData);  // "object" 여야 함
console.log(employmentData);          // 올바른 객체가 출력되어야 함

// 데이터 내에서 null 값 확인 (Python None이 아님)
console.log(employmentData.datasets[0].data);  // null 값이 있다면 null로 표시
```

### 5. 자동화된 검증 스크립트

터미널에서 실행:

```bash
# JSON 인코딩 검증
python verify_json_encoding.py

# Serializers 테스트
python test_serialization.py
```

## 예상 결과

### ✓ 성공 케이스

**이전 (잘못된 형식):**
```javascript
const data = {'labels': ['A', 'B'], 'data': [None, 10], 'fill': False};
// ✗ Python dict/literal 형식, JavaScript에서 에러 발생
```

**현재 (올바른 형식):**
```javascript
const data = {"labels": ["A", "B"], "data": [null, 10], "fill": false};
// ✓ 올바른 JSON 형식, JavaScript에서 정상 작동
```

### ✓ 타입 변환 확인

| Python 타입 | JSON 결과 | JavaScript 타입 |
|------------|-----------|-----------------|
| `None`     | `null`    | `null`          |
| `True`     | `true`    | `true`          |
| `False`    | `false`   | `false`         |
| `"text"`   | `"text"`  | `"text"`        |
| `123`      | `123`     | `123`           |
| `123.45`   | `123.45`  | `123.45`        |

## 문제 해결 완료 확인

모든 체크박스에 체크하고 JavaScript 에러가 없다면 ✓ **문제 해결 완료!**

## 추가 개선 사항

현재는 데이터만 전달하고 있으므로, 실제로 차트를 렌더링하려면 템플릿에 Chart.js 초기화 코드 추가가 필요합니다:

```javascript
// 예시: dashboard.html
const ctx = document.getElementById('employmentChart').getContext('2d');
new Chart(ctx, {
    type: 'bar',
    data: employmentData,  // json.dumps()로 직렬화된 데이터
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: 'Employment Rate by Department'
            }
        }
    }
});
```

이것은 별도의 작업이며, 현재 작업 범위(직렬화 문제 해결)와는 별개입니다.
