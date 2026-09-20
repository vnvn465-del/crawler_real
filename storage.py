# =========================
# storage.py
# DB 연결 / 테이블 생성 / 저장 역할
# =========================

# SQLite 사용을 위한 내장 모듈
import sqlite3


# SQLite DB 연결 함수
def connect_db(db_path):
    # db_path에 해당하는 SQLite 파일 연결
    return sqlite3.connect(db_path)


# 필요한 테이블 생성 함수
def create_tables(cur):
    # 상품 기본 정보 테이블
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,   -- 상품 고유 ID
            name TEXT NOT NULL             -- 상품명
        )
    """)

    # 날짜별 상품 상태 스냅샷 테이블
    cur.execute("""
        CREATE TABLE IF NOT EXISTS product_snapshots (
            product_id TEXT NOT NULL,         -- 상품 ID
            snapshot_date TEXT NOT NULL,      -- 수집 날짜
            rank INTEGER NOT NULL,            -- 순위
            price INTEGER NOT NULL,           -- 가격
            review_count INTEGER NOT NULL,    -- 리뷰 수
            PRIMARY KEY (product_id, snapshot_date),  -- 같은 날짜 중복 저장 방지
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)


# 파싱한 상품 목록 저장 함수
def save_items(cur, items, snapshot_date):
    # 상품 목록 하나씩 저장
    for item in items:
        # 상품 기본 정보 저장
        # 같은 product_id가 이미 있으면 무시
        cur.execute(
            """
            INSERT OR IGNORE INTO products (product_id, name)
            VALUES (?, ?)
            """,
            (item["product_id"], item["name"])
        )

        # 날짜별 스냅샷 저장
        # 같은 상품 + 같은 날짜가 이미 있으면 교체
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


# 특정 날짜의 스냅샷 조회 함수
def get_snapshot_by_date(cur, snapshot_date):
    # 상품 이름까지 함께 보기 위해 products와 join
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
        ORDER BY ps.rank ASC
        """,
        (snapshot_date,)
    ).fetchall()

    return rows
