# =========================
# compare.py
# 두 날짜의 스냅샷을 비교하는 파일
# =========================

# DB 연결 함수 import
from storage import connect_db
from config import DB_PATH


# 특정 날짜의 스냅샷을 dict 형태로 불러오는 함수
def load_snapshot(cur, snapshot_date):
    # products와 product_snapshots를 join해서
    # 상품명까지 포함한 데이터를 가져옴
    rows = cur.execute(
        """
        SELECT
            ps.product_id,
            p.name,
            ps.rank,
            ps.price,
            ps.review_count
        FROM product_snapshots ps
        JOIN products p
          ON ps.product_id = p.product_id
        WHERE ps.snapshot_date = ?
        """,
        (snapshot_date,)
    ).fetchall()

    # 비교하기 쉽게 product_id를 key로 하는 dict로 변환
    snapshot = {}

    for row in rows:
        product_id, name, rank, price, review_count = row

        snapshot[product_id] = {
            "product_id": product_id,
            "name": name,
            "rank": rank,
            "price": price,
            "review_count": review_count,
        }

    return snapshot


# DB에 저장된 날짜 목록을 가져오는 함수
def get_snapshot_dates(cur):
    # 중복 없는 날짜를 오름차순으로 조회
    rows = cur.execute(
        """
        SELECT DISTINCT snapshot_date
        FROM product_snapshots
        ORDER BY snapshot_date ASC
        """
    ).fetchall()

    # [('2026-09-20',), ('2026-09-21',)] -> ['2026-09-20', '2026-09-21']
    return [row[0] for row in rows]


# 메인 실행 함수
def main():
    # 1) DB 연결
    conn = connect_db(DB_PATH)
    cur = conn.cursor()

    # 2) 저장된 날짜 목록 조회
    dates = get_snapshot_dates(cur)

    # 3) 최소 2개 날짜가 있어야 비교 가능
    if len(dates) < 2:
        print("비교할 날짜가 2개 이상 필요합니다.")
        print("pipeline.py를 날짜를 바꿔 2번 이상 실행하세요.")
        conn.close()
        return

    # 4) 가장 최근 2개 날짜를 비교 대상으로 선택
    old_date = dates[-2]
    new_date = dates[-1]

    print(f"비교 대상: {old_date} -> {new_date}\n")

    # 5) 각 날짜 스냅샷 로드
    old_snapshot = load_snapshot(cur, old_date)
    new_snapshot = load_snapshot(cur, new_date)

    # 6) product_id 집합 생성
    old_ids = set(old_snapshot.keys())
    new_ids = set(new_snapshot.keys())

    # 7) 신규/삭제/공통 상품 구분
    added_ids = sorted(new_ids - old_ids)
    removed_ids = sorted(old_ids - new_ids)
    common_ids = sorted(old_ids & new_ids)

    # =========================
    # 신규 상품 출력
    # =========================
    print("[신규 상품]")
    if added_ids:
        for product_id in added_ids:
            item = new_snapshot[product_id]
            print(
                f"- {item['product_id']} / {item['name']} / "
                f"rank={item['rank']} / price={item['price']} / reviews={item['review_count']}"
            )
    else:
        print("- 없음")

    print()

    # =========================
    # 삭제 상품 출력
    # =========================
    print("[삭제 상품]")
    if removed_ids:
        for product_id in removed_ids:
            item = old_snapshot[product_id]
            print(
                f"- {item['product_id']} / {item['name']} / "
                f"rank={item['rank']} / price={item['price']} / reviews={item['review_count']}"
            )
    else:
        print("- 없음")

    print()

    # =========================
    # 가격 변동 출력
    # =========================
    print("[가격 변동]")
    price_changed = False

    for product_id in common_ids:
        old_item = old_snapshot[product_id]
        new_item = new_snapshot[product_id]

        old_price = old_item["price"]
        new_price = new_item["price"]

        if old_price != new_price:
            price_changed = True
            diff = new_price - old_price

            if diff > 0:
                print(
                    f"- {new_item['product_id']} / {new_item['name']} : "
                    f"{old_price} -> {new_price} (▲ {diff})"
                )
            else:
                print(
                    f"- {new_item['product_id']} / {new_item['name']} : "
                    f"{old_price} -> {new_price} (▼ {abs(diff)})"
                )

    if not price_changed:
        print("- 없음")

    print()

    # =========================
    # 순위 변동 출력
    # =========================
    print("[순위 변동]")
    rank_changed = False

    for product_id in common_ids:
        old_item = old_snapshot[product_id]
        new_item = new_snapshot[product_id]

        old_rank = old_item["rank"]
        new_rank = new_item["rank"]

        if old_rank != new_rank:
            rank_changed = True

            # 숫자가 작아질수록 더 높은 순위
            if new_rank < old_rank:
                print(
                    f"- {new_item['product_id']} / {new_item['name']} : "
                    f"{old_rank}위 -> {new_rank}위 (순위 상승)"
                )
            else:
                print(
                    f"- {new_item['product_id']} / {new_item['name']} : "
                    f"{old_rank}위 -> {new_rank}위 (순위 하락)"
                )

    if not rank_changed:
        print("- 없음")

    print()

    # =========================
    # 리뷰 수 변동 출력
    # =========================
    print("[리뷰 수 변동]")
    review_changed = False

    for product_id in common_ids:
        old_item = old_snapshot[product_id]
        new_item = new_snapshot[product_id]

        old_reviews = old_item["review_count"]
        new_reviews = new_item["review_count"]

        if old_reviews != new_reviews:
            review_changed = True
            diff = new_reviews - old_reviews

            if diff > 0:
                print(
                    f"- {new_item['product_id']} / {new_item['name']} : "
                    f"{old_reviews} -> {new_reviews} (▲ {diff})"
                )
            else:
                print(
                    f"- {new_item['product_id']} / {new_item['name']} : "
                    f"{old_reviews} -> {new_reviews} (▼ {abs(diff)})"
                )

    if not review_changed:
        print("- 없음")

    # 8) DB 연결 종료
    conn.close()


# 직접 실행 시 main() 호출
if __name__ == "__main__":
    main()
