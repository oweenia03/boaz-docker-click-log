"""
클릭 로그 수집 API

- POST /events    : 클릭 로그 1건 저장
- POST /simulate  : 랜덤 클릭 로그 n건 생성
- GET  /stats     : 페이지별 / 기기별 클릭 수

DB 접속 정보는 전부 환경변수(compose.yaml의 environment)에서 읽어 온다.
"""

import os
import random
import socket
from datetime import datetime, timedelta, timezone

import psycopg
from fastapi import FastAPI, Query
from pydantic import BaseModel

# compose.yaml의 api > environment 에 적힌 값을 읽는다.
# DB_HOST에는 localhost가 아니라 서비스 이름(postgres)이 들어간다.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "clicks"),
    "user": os.getenv("DB_USER", "app"),
    "password": os.getenv("DB_PASSWORD", ""),
}

PAGES = ["home", "search", "product", "cart", "checkout"]
PAGE_WEIGHTS = [40, 25, 20, 10, 5]
DEVICES = ["mobile", "desktop", "tablet"]
DEVICE_WEIGHTS = [60, 30, 10]

app = FastAPI(title="Click Log API", description="Docker 실습용 클릭 로그 수집 API")


def get_conn():
    # 요청마다 새로 연결한다. postgres 컨테이너가 새로 만들어져도 다음 요청부터 바로 다시 붙는다.
    return psycopg.connect(**DB_CONFIG)


class Event(BaseModel):
    user_name: str
    page: str = "home"
    device: str = "mobile"


@app.get("/")
def root():
    return {
        "message": "Click Log API is running",
        "docs": "/docs",
        "served_by": socket.gethostname(),  # 이 요청을 처리한 컨테이너 ID
    }


@app.post("/events")
def create_event(event: Event):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO events (user_name, page, device) VALUES (%s, %s, %s)",
            (event.user_name, event.page, event.device),
        )
    return {"saved": event.model_dump()}


@app.post("/simulate")
def simulate(n: int = Query(500, ge=1, le=5000, description="생성할 로그 개수")):
    now = datetime.now(timezone.utc)
    rows = [
        (
            f"user_{random.randint(1, 50):02d}",
            random.choices(PAGES, weights=PAGE_WEIGHTS)[0],
            random.choices(DEVICES, weights=DEVICE_WEIGHTS)[0],
            now - timedelta(minutes=random.randint(0, 7 * 24 * 60)),  # 최근 7일 사이
        )
        for _ in range(n)
    ]
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO events (user_name, page, device, created_at) VALUES (%s, %s, %s, %s)",
                rows,
            )
    return {"inserted": n}


@app.get("/stats")
def stats():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        by_page = conn.execute(
            "SELECT page, COUNT(*) FROM events GROUP BY page ORDER BY COUNT(*) DESC"
        ).fetchall()
        by_device = conn.execute(
            "SELECT device, COUNT(*) FROM events GROUP BY device ORDER BY COUNT(*) DESC"
        ).fetchall()
    return {
        "total": total,
        "by_page": dict(by_page),
        "by_device": dict(by_device),
    }
