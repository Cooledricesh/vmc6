#!/bin/bash

echo "🚀 개발 환경 시작 스크립트"
echo "================================"

# 1. Docker 상태 확인
echo "1️⃣ Docker 상태 확인..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker가 실행되지 않았습니다."
    echo "👉 Docker Desktop을 시작하세요: open -a Docker"
    echo "👉 1-2분 대기 후 다시 실행하세요."
    exit 1
fi
echo "✅ Docker 실행 중"

# 2. Supabase 시작
echo "2️⃣ Supabase 로컬 DB 시작..."
supabase start
echo "✅ Supabase 시작 완료"

# 3. 가상환경 활성화
echo "3️⃣ Python 가상환경 활성화..."
cd /Users/seunghyun/Test/vmc6
source venv/bin/activate
echo "✅ 가상환경 활성화 완료"

# 4. DB 상태 확인
echo "4️⃣ DB 연결 테스트..."
python -c "
from django.conf import settings
import psycopg2
try:
    conn = psycopg2.connect(
        host='127.0.0.1',
        port=54322,
        database='postgres',
        user='postgres',
        password='postgres'
    )
    conn.close()
    print('✅ DB 연결 성공')
except Exception as e:
    print(f'❌ DB 연결 실패: {e}')
"

echo "================================"
echo "✅ 개발 환경 준비 완료!"
echo ""
echo "테스트 실행:"
echo "  python manage.py test apps.authentication.tests.test_models"
echo ""
echo "개발 서버 시작:"
echo "  python manage.py runserver"
echo ""
echo "Supabase Studio:"
echo "  http://127.0.0.1:54323"