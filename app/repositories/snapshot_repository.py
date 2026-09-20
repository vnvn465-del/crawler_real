# =========================
# app/repositories/snapshot_repository.py
# DB CRUD 담당
# =========================

# products, product_snapshots 테이블 생성
def create_tables(conn):
    # 커서 생성
    cur = conn.cursor()

    # 상품 기본 정보 테이블 생성
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    # 날짜별 상품 스냅샷 테이블 생성
    cur.execute("""
        CREATE TABLE IF NOT EXISTS product_snapshots (
            product_id TEXT NOT NULL,
            snapshot_date TEXT NOT NULL,
            rank INTEGER NOT NULL,
            price INTEGER NOT NULL,
            review_count INTEGER,
            PRIMARY KEY (product_id, snapshot_date),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    # DB 반영
    conn.commit()


# 상품 목록을 저장하는 함수
def save_items(conn, items: list[dict], snapshot_date: str):
    # 커서 생성
    cur = conn.cursor()

    # 각 상품 저장
    for item in items:
        # 상품 기본 정보 저장
        cur.execute(
            """
            INSERT OR IGNORE INTO products (product_id, name)
            VALUES (?, ?)
            """,
            (item["product_id"], item["name"])
        )

        # 날짜별 스냅샷 저장
        cur.execute(
            """
            INSERT OR REPLACE INTO product_snapshots
            (product_id, snapshot_date, rank, price, review_count)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                item["product_id"],
                snapshot_date,
                item["rank"],
                item["price"],
                item["review_count"],
            )
        )

    # DB 반영
    conn.commit()


# 저장된 날짜 목록 조회
def get_snapshot_dates(conn) -> list[str]:
    # 커서 생성
    cur = conn.cursor()

    # 날짜 목록 조회
    rows = cur.execute(
        """
        SELECT DISTINCT snapshot_date
        FROM product_snapshots
        ORDER BY snapshot_date ASC
        """
    ).fetchall()

    # 문자열 리스트로 변환
    return [row["snapshot_date"] for row in rows]


# 특정 날짜의 스냅샷 상세 조회
def get_snapshot_rows(conn, snapshot_date: str) -> list[dict]:
    # 커서 생성
    cur = conn.cursor()

    # 상품명까지 join해서 조회
    rows = cur.execute(
        """
        SELECT
            ps.product_id,
            p.name,
            ps.snapshot_date,
            ps.rank,
            ps.price,
            ps.review_count
        FROM product_snapshots ps
        JOIN products p
          ON ps.product_id = p.product_id
        WHERE ps.snapshot_date = ?
        ORDER BY ps.rank ASC
        """,
        (snapshot_date,)
    ).fetchall()

    # sqlite Row -> dict 변환
    return [dict(row) for row in rows]


# 특정 날짜의 스냅샷을 product_id 기준 dict로 변환
def get_snapshot_map(conn, snapshot_date: str) -> dict:
    # 상세 rows 조회
    items = get_snapshot_rows(conn, snapshot_date)

    # product_id를 key로 변환
    return {item["product_id"]: item for item in items}
