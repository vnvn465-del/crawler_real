# =========================
# app/services/compare_service.py
# 날짜별 비교 비즈니스 로직
# =========================

# DB 연결 import
from app.db.database import get_connection

# repository import
from app.repositories.snapshot_repository import get_snapshot_dates, get_snapshot_map


# 두 날짜를 비교하는 함수
def compare_two_snapshots(old_date: str, new_date: str) -> dict | None:
    # DB 연결
    conn = get_connection()

    try:
        # 각 날짜의 스냅샷을 product_id 기준 dict로 조회
        old_snapshot = get_snapshot_map(conn, old_date)
        new_snapshot = get_snapshot_map(conn, new_date)

    finally:
        # 연결 종료
        conn.close()

    # 둘 중 하나라도 없으면 None
    if not old_snapshot or not new_snapshot:
        return None

    # 상품 ID 집합 생성
    old_ids = set(old_snapshot.keys())
    new_ids = set(new_snapshot.keys())

    # 신규 / 삭제 / 공통 상품 분리
    added_ids = sorted(new_ids - old_ids)
    removed_ids = sorted(old_ids - new_ids)
    common_ids = sorted(old_ids & new_ids)

    # 신규 상품 리스트
    added_items = [new_snapshot[product_id] for product_id in added_ids]

    # 삭제 상품 리스트
    removed_items = [old_snapshot[product_id] for product_id in removed_ids]

    # 가격 변동 리스트
    price_changes = []

    # 순위 변동 리스트
    rank_changes = []

    # 리뷰 수 변동 리스트
    review_changes = []

    # 공통 상품 비교
    for product_id in common_ids:
        old_item = old_snapshot[product_id]
        new_item = new_snapshot[product_id]

        # 가격 비교
        if old_item["price"] != new_item["price"]:
            price_changes.append({
                "product_id": product_id,
                "name": new_item["name"],
                "old_price": old_item["price"],
                "new_price": new_item["price"],
                "diff": new_item["price"] - old_item["price"],
            })

        # 순위 비교
        if old_item["rank"] != new_item["rank"]:
            rank_changes.append({
                "product_id": product_id,
                "name": new_item["name"],
                "old_rank": old_item["rank"],
                "new_rank": new_item["rank"],
                "diff": new_item["rank"] - old_item["rank"],
                "direction": "up" if new_item["rank"] < old_item["rank"] else "down",
            })

        # 리뷰 수 비교
        if old_item["review_count"] != new_item["review_count"]:
            review_changes.append({
                "product_id": product_id,
                "name": new_item["name"],
                "old_review_count": old_item["review_count"],
                "new_review_count": new_item["review_count"],
                "diff": new_item["review_count"] - old_item["review_count"],
            })

    # 최종 비교 결과 반환
    return {
        "old_date": old_date,
        "new_date": new_date,
        "added": added_items,
        "removed": removed_items,
        "price_changes": price_changes,
        "rank_changes": rank_changes,
        "review_changes": review_changes,
    }


# 최신 2개 날짜를 자동으로 비교하는 함수
def compare_latest_snapshots() -> dict | None:
    # DB 연결
    conn = get_connection()

    try:
        # 날짜 목록 조회
        dates = get_snapshot_dates(conn)

    finally:
        # 연결 종료
        conn.close()

    # 비교하려면 최소 2개 날짜 필요
    if len(dates) < 2:
        return None

    # 최근 2개 날짜 선택
    old_date = dates[-2]
    new_date = dates[-1]

    # 두 날짜 비교
    return compare_two_snapshots(old_date, new_date)
