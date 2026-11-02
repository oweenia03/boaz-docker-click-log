# 1) 출발점: Python 3.11이 설치된 가벼운 리눅스 이미지
FROM python:3.11-slim

# 2) 이미지 안에서 작업할 폴더
WORKDIR /app

# 3) 라이브러리 목록을 먼저 복사하고 설치 (잘 안 바뀌는 것 → 위쪽, 레이어 캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) 자주 바뀌는 코드는 나중에 복사
COPY main.py .

# 5) 이 컨테이너가 8000번 포트를 쓴다는 "메모" (실제 연결은 compose의 ports)
EXPOSE 8000

# 6) 컨테이너가 시작될 때 실행할 명령 (0.0.0.0 = 컨테이너 밖에서 온 요청도 받기)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
