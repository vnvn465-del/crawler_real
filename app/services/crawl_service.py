# =========================
# app/services/crawl_service.py
# 수집 + 파싱 + 저장 비즈니스 로직
# =========================

from datetime import date

from app.core.config import TARGET_URL, FETCH_MODE, SNAPSHOT_DATE
from app.db.database import get_connection
from app.repositories.snapshot_repository import create_tables, save_items, get_snapshot_rows
from app.crawler.fetcher import fetch_html
from app.crawler.parser import parse_products


def get_html_by_mode(url: str) -> str:
    if FETCH_MODE == "httpx":
        return fetch_html(url)

    if FETCH_MODE == "playwright":
        # 필요할 때만 import — 미설치 환경에서도 httpx 모드는 살아 있게
        from app.crawler.playwright_fetch import fetch_html_with_playwright
        return fetch_html_with_playwright(url)

    raise ValueError(f"지원하지 않는 FETCH_MODE입니다: {FETCH_MODE}")


def collect_items(url: str = TARGET_URL) -> list[dict]:
    html = get_html_by_mode(url)
    items = parse_products(html)
    return items


def collect_and_save_snapshot(snapshot_date: str | None = None) -> dict:
    target_date = snapshot_date or SNAPSHOT_DATE or date.today().isoformat()

    # 1) 수집 + 파싱을 먼저 끝낸다.
    #    여기서 실패하면(ParseError) DB를 아예 건드리지 않는다.
    items = collect_items(TARGET_URL)

    conn = get_connection()

    try:
        create_tables(conn)
        save_items(conn, items, target_date)
        saved_items = get_snapshot_rows(conn, target_date)

    except Exception:
        # 2) 저장 도중 문제가 생기면 부분 저장을 남기지 않는다
        conn.rollback()
        raise          # 3) 예외를 위로 올려보낸다 (삼키면 실패가 성공으로 둔갑)

    finally:
        conn.close()

    return {
        "snapshot_date": target_date,
        "count": len(saved_items),
        "fetch_mode": FETCH_MODE,
        "items": saved_items,
    }
