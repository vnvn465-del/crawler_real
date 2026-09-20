# =========================
# app/services/crawl_service.py
# 수집 + 파싱 + 저장 비즈니스 로직
# =========================

from datetime import date

from app.core.config import TARGET_URL, FETCH_MODE, SNAPSHOT_DATE
from app.db.database import get_connection
from app.repositories.snapshot_repository import create_tables, save_items, get_snapshot_rows
from app.crawler.fetcher import fetch_html
from app.crawler.playwright_fetch import fetch_html_with_playwright
from app.crawler.parser import parse_products


def get_html_by_mode(url: str) -> str:
    if FETCH_MODE == "httpx":
        return fetch_html(url)

    if FETCH_MODE == "playwright":
        return fetch_html_with_playwright(url)

    raise ValueError(f"지원하지 않는 FETCH_MODE입니다: {FETCH_MODE}")


def collect_items(url: str = TARGET_URL) -> list[dict]:
    html = get_html_by_mode(url)
    items = parse_products(html)
    return items


def collect_and_save_snapshot(snapshot_date: str | None = None) -> dict:
    target_date = snapshot_date or SNAPSHOT_DATE or date.today().isoformat()
    items = collect_items(TARGET_URL)

    conn = get_connection()

    try:
        create_tables(conn)
        save_items(conn, items, target_date)
        saved_items = get_snapshot_rows(conn, target_date)
    finally:
        conn.close()

    return {
        "snapshot_date": target_date,
        "count": len(saved_items),
        "fetch_mode": FETCH_MODE,
        "items": saved_items,
    }
