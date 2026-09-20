# =========================
# app/main.py
# FastAPI 앱 시작점
# =========================

# lifespan 사용을 위한 모듈
from contextlib import asynccontextmanager

# FastAPI import
from fastapi import FastAPI

# DB 관련 import
from app.db.database import get_connection
from app.repositories.snapshot_repository import create_tables

# controller import
from app.controllers.health_controller import router as health_router
from app.controllers.snapshot_controller import router as snapshot_router
from app.controllers.compare_controller import router as compare_router


# 앱 시작 시 한 번 실행할 초기화 로직
@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB 연결
    conn = get_connection()

    try:
        # 테이블 없으면 생성
        create_tables(conn)
    finally:
        # 초기화 후 연결 종료
        conn.close()

    # 앱 실행
    yield


# FastAPI 앱 생성
app = FastAPI(
    title="Crawler API",
    lifespan=lifespan,
)

# 라우터 등록
app.include_router(health_router)
app.include_router(snapshot_router)
app.include_router(compare_router)
