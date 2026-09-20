# =========================
# app/services/snapshot_service.py
# 스냅샷 조회 비즈니스 로직
# =========================

# DB 연결 import
from app.db.database import get_connection

# repository import
from app.repositories.snapshot_repository import get_snapshot_dates, get_snapshot_rows


# 저장된 날짜 목록 조회
def list_snapshot_dates() -> list[str]:
    # DB 연결
    conn = get_connection()

    try:
        # 날짜 목록 반환
        return get_snapshot_dates(conn)

    finally:
        # 연결 종료
        conn.close()


# 특정 날짜 스냅샷 조회
def get_snapshot_by_date(snapshot_date: str) -> dict | None:
    # DB 연결
    conn = get_connection()

    try:
        # 해당 날짜 데이터 조회
        items = get_snapshot_rows(conn, snapshot_date)

    finally:
        # 연결 종료
        conn.close()

    # 데이터 없으면 None
    if not items:
        return None

    # 응답 형식으로 반환
    return {
        "snapshot_date": snapshot_date,
        "count": len(items),
        "items": items,
    }


# 가장 최신 날짜 스냅샷 조회
def get_latest_snapshot() -> dict | None:
    # DB 연결
    conn = get_connection()

    try:
        # 날짜 목록 조회
        dates = get_snapshot_dates(conn)

        # 날짜가 없으면 None
        if not dates:
            return None

        # 최신 날짜 선택
        latest_date = dates[-1]

        # 최신 날짜 데이터 조회
        items = get_snapshot_rows(conn, latest_date)

    finally:
        # 연결 종료
        conn.close()

    return {
        "snapshot_date": latest_date,
        "count": len(items),
        "items": items,
    }
