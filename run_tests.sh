#!/bin/bash

# Django 테스트 실행 스크립트
cd /Users/seunghyun/Test/vmc6

# 가상환경 활성화
source venv/bin/activate

echo "🚀 Django TDD 테스트 시작"
echo "================================"

# Phase 1: User 모델 테스트
echo "📝 Phase 1: User 모델 테스트 실행..."
python manage.py test apps.authentication.tests.test_models

# 다른 테스트 실행 예시
# echo "📝 Phase 2: SignupForm 테스트..."
# python manage.py test apps.authentication.tests.test_forms.SignupFormTest

echo "================================"
echo "✅ 테스트 완료"