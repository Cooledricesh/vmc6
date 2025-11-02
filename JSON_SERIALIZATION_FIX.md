# Fix: Python to JavaScript Serialization Error

**Date:** 2025-11-03
**Status:** ✓ COMPLETED
**Issue:** JavaScript errors due to Python literals in chart data

---

## 문제 상황

사용자가 analytics 페이지들을 방문했을 때 JavaScript 에러가 발생하여 차트가 표시되지 않음:

### 에러 메시지

1. `The specified value "None" cannot be parsed`
2. `ReferenceError: False is not defined`
3. `ReferenceError: True is not defined`

### 근본 원인

- Django 템플릿에서 `{{ chart_data|safe }}`를 사용할 때, Python 딕셔너리가 그대로 출력됨
- Python 리터럴 (`None`, `True`, `False`)이 JavaScript에서 인식되지 않음

---

## 해결 방법

### 수정된 파일

**파일:** `/Users/seunghyun/Test/vmc6/apps/analytics/views.py`

### 핵심 변경사항

모든 view 함수에서 chart 데이터를 context에 추가할 때 **`json.dumps()`로 감쌌습니다.**

#### 1. dashboard_view (145-147줄)

```python
# BEFORE
context = {
    'employment_chart_data': employment_chart_data,
    'publication_chart_data': publication_chart_data,
    'budget_chart_data': budget_chart_data,
}

# AFTER
context = {
    'employment_chart_data': json.dumps(employment_chart_data),
    'publication_chart_data': json.dumps(publication_chart_data),
    'budget_chart_data': json.dumps(budget_chart_data),
}
```

#### 2. department_kpi_view (212-213줄)

```python
context = {
    'kpi_trend_data': json.dumps(kpi_trend_data),
    'department_comparison_data': json.dumps(department_comparison_data),
    'selected_year': selected_year,
}
```

#### 3. publications_view (268-269줄)

```python
context = {
    'grade_distribution_data': json.dumps(grade_distribution_data),
    'department_publication_data': json.dumps(department_publication_data),
}
```

#### 4. research_budget_view (337-338줄)

```python
context = {
    'execution_rate_data': json.dumps(execution_rate_data),
    'category_distribution_data': json.dumps(category_distribution_data),
}
```

#### 5. students_view (396-397줄)

```python
context = {
    'total_students': total_students,
    'enrollment_by_year_data': json.dumps(enrollment_by_year_data),
    'department_distribution_data': json.dumps(department_distribution_data),
}
```

---

## 왜 이것이 작동하는가?

### Python to JSON 타입 변환

`json.dumps()`는 Python 객체를 JSON 문자열로 변환하며, 타입 변환을 자동으로 처리합니다:

| Python 타입 | JSON 결과 | JavaScript 타입 |
|------------|-----------|-----------------|
| `None`     | `null`    | `null`          |
| `True`     | `true`    | `true`          |
| `False`    | `false`   | `false`         |
| `str`      | `"..."`   | `string`        |
| `int`      | `123`     | `number`        |
| `float`    | `123.45`  | `number`        |
| `list`     | `[...]`   | `Array`         |
| `dict`     | `{...}`   | `Object`        |

### 템플릿 렌더링 비교

#### ❌ Before (잘못된 방식)

```python
# views.py
context = {
    'chart_data': {'labels': ['A', 'B'], 'data': [None, 10], 'fill': False}
}
```

```html
<!-- template.html -->
<script>
    const chartData = {{ chart_data|safe }};
    // 결과: const chartData = {'labels': ['A', 'B'], 'data': [None, 10], 'fill': False};
    // ✗ JavaScript Error!
</script>
```

#### ✓ After (올바른 방식)

```python
# views.py
import json

context = {
    'chart_data': json.dumps({'labels': ['A', 'B'], 'data': [None, 10], 'fill': False})
}
```

```html
<!-- template.html -->
<script>
    const chartData = {{ chart_data|safe }};
    // 결과: const chartData = {"labels": ["A", "B"], "data": [null, 10], "fill": false};
    // ✓ Valid JavaScript!
</script>
```

---

## 테스트 방법

### 자동 검증 스크립트

```bash
cd /Users/seunghyun/Test/vmc6

# JSON 인코딩 검증
python verify_json_encoding.py

# 최종 검증 (템플릿 렌더링 시뮬레이션)
python final_verification.py
```

### 브라우저 수동 테스트

**간단 테스트:**

1. 서버 실행: `python manage.py runserver`
2. 브라우저에서 http://127.0.0.1:8000/login/ 접속
3. 로그인 (test_admin@example.com / testpass123)
4. 각 analytics 페이지 방문하여 F12 Console 확인

**테스트할 페이지:**
- http://127.0.0.1:8000/dashboard/
- http://127.0.0.1:8000/analytics/department-kpi/
- http://127.0.0.1:8000/analytics/publications/
- http://127.0.0.1:8000/analytics/research-budget/
- http://127.0.0.1:8000/analytics/students/

### 확인 사항

브라우저 Console (F12)에서:

```javascript
// 변수가 올바르게 정의되었는지 확인
console.log(typeof employmentData);  // "object"
console.log(employmentData);          // 올바른 객체 출력

// null 값 확인 (None이 아님)
console.log(employmentData.datasets[0].data);  // [..., null, ...]
```

페이지 소스 (`Ctrl+U`)에서:

```javascript
// ✓ 올바른 형식:
const chartData = {"labels":["CS","Math"],"datasets":[{"data":[85,null,90],"fill":false}]};

// ✗ 잘못된 형식 (이런 것이 보이면 안 됨):
const chartData = {'labels': ['CS', 'Math'], 'data': [None, 10], 'fill': False};
```

---

## 영향 범위

### 수정된 View Functions (5개)

1. ✓ `dashboard_view` - 3개 차트 데이터
2. ✓ `department_kpi_view` - 2개 차트 데이터
3. ✓ `publications_view` - 2개 차트 데이터
4. ✓ `research_budget_view` - 2개 차트 데이터
5. ✓ `students_view` - 2개 차트 데이터

### 영향받는 템플릿 (5개)

템플릿은 변경 **불필요** - 이미 `{{ variable|safe }}` 형식으로 올바르게 작성되어 있음

- `templates/analytics/dashboard.html`
- `templates/analytics/department_kpi.html`
- `templates/analytics/publications.html`
- `templates/analytics/research_budget.html`
- `templates/analytics/students.html`

---

## 생성된 테스트 파일

테스트 및 검증을 위해 다음 파일들이 생성되었습니다 (프로젝트 실행에는 영향 없음):

1. `verify_json_encoding.py` - JSON 인코딩 검증
2. `test_serialization.py` - Serializers 테스트
3. `final_verification.py` - 템플릿 렌더링 시뮬레이션
4. `test_pages.py` - Django test client 기반 테스트
5. `quick_test.py` - 빠른 검증 스크립트
6. `TESTING_CHECKLIST.md` - 수동 테스트 체크리스트
7. `JSON_SERIALIZATION_FIX.md` - 이 문서

---

## 추가 참고사항

### serializers.py는 수정 불필요

`apps/analytics/serializers.py`의 함수들은 이미 올바르게 구현되어 있습니다:

- `_convert_value()` 함수가 Decimal, None 등을 처리
- Python 객체를 JSON-serializable 타입으로 변환
- `json.dumps()`와 함께 사용하면 완벽하게 작동

### 템플릿의 `|safe` 필터는 유지

- `json.dumps()`가 JSON 문자열을 생성
- `|safe` 필터가 HTML 이스케이프를 방지
- 결과: 올바른 JavaScript 객체 리터럴

### 일반 데이터는 json.dumps() 불필요

```python
# 이런 것들은 그대로 사용 가능 (json.dumps 불필요)
context = {
    'total_students': 150,           # int
    'department_name': 'CS',         # str
    'avg_rate': 85.5,                # float
    'selected_year': 2024,           # int
}

# JavaScript로 전달할 객체/배열만 json.dumps() 필요
context = {
    'chart_data': json.dumps({...}),      # dict → JSON
    'data_list': json.dumps([...]),       # list → JSON
    'config': json.dumps({...}),          # complex object → JSON
}
```

---

## 결론

✓ **모든 analytics views 수정 완료**
✓ **Python → JSON → JavaScript 변환 정상 작동**
✓ **JavaScript 에러 해결**
✓ **차트 데이터 올바른 형식으로 전달**

이제 브라우저에서 테스트하여 차트가 정상적으로 표시되는지 확인하세요!

---

**Modified by:** Claude Code
**Issue:** Python to JavaScript serialization error
**Solution:** Wrap all chart data with `json.dumps()` in views
