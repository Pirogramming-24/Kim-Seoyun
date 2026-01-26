# 1. 파이썬 설치 (가벼운 슬림 버전)
FROM python:3.13-slim

# 2. 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# 3. 환경 변수 설정 (파이썬 로그가 즉시 출력되도록 함)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 4. 필수 라이브러리 설치
RUN apt-get update && apt-get install -y libpq-dev gcc

# 5. 의존성 파일 복사 및 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 6. 전체 프로젝트 코드 복사
COPY . /app/

# 7. 서버 실행 명령 (8000 포트)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]