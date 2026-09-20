# =========================
# app/db/database.py
# DB 연결 관리
# =========================

# SQLite 사용을 위한 모듈 import
import sqlite3

# 설정값 import
from app.core.config import DB_PATH


# SQLite 연결을 반환하는 함수
def get_connection():
    # SQLite DB 파일 연결
    conn = sqlite3.connect(DB_PATH)

    # row를 dict처럼 다루기 쉽게 Row factory 설정
    conn.row_factory = sqlite3.Row

    return conn
