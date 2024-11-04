# 기반 이미지 설정
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치 (OpenCV와 관련 라이브러리 설치)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean

# 프로젝트 의존성 파일 복사
COPY pyproject.toml poetry.lock /app/

# Poetry 설치 및 의존성 설치
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-root

# 애플리케이션 소스 코드 복사
COPY . /app

# Gunicorn을 사용하여 FastAPI 애플리케이션 실행
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8200", "--workers", "2"]
