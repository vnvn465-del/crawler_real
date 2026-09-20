# =========================
# app/repositories/snapshot_repository.py
# DB CRUD 담당 (Repository 계층)
#   -> Java 의 JpaRepository / DAO. "DB와 대화"만 하고 비즈니스 로직은 없다.
# =========================


# ---------------------------------------------------------
# 테이블 생성
# ---------------------------------------------------------
# products          : 변하지 않는 상품 기본 정보 (이름)
# product_snapshots : 날짜별로 변하는 값 (순위/가격/리뷰수)
# ---------------------------------------------------------
def create_tables(conn):
    cur = conn.cursor()

    # ---- (1) 상품 기본 정보 ----
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    # ---- (2) 날짜별 스냅샷 ----
    # PRIMARY KEY (product_id, snapshot_date)
    #   -> "한 상품은 하루에 한 행" 을 DB가 강제한다 (앱 버그로도 중복 안 생김)
    #
    # review_count 는 NULL 허용:
    #   0    = 리뷰가 진짜 0개 (신상품)
    #   NULL = 리뷰 수를 못 읽음 (모른다)
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

    conn.commit()


# ---------------------------------------------------------
# 상품 목록 저장 (오늘의 스냅샷)
# ---------------------------------------------------------
def save_items(conn, items: list[dict], snapshot_date: str):
    cur = conn.cursor()

    for item in items:
        # ---- (1) 상품 기본 정보 ----
        # INSERT OR IGNORE: 이미 있는 상품이면 조용히 넘어간다.
        cur.execute(
            """
            INSERT OR IGNORE INTO products (product_id, name)
            VALUES (?, ?)
            """,
            (item["product_id"], item["name"])
        )

        # ---- (2) 날짜별 스냅샷 ----
        # ON CONFLICT DO UPDATE 는 진짜 UPDATE 다. 적어둔 컬럼만 바뀐다.
        # ON CONFLICT(...) 안에는 위 PRIMARY KEY 와 "정확히 같은 조합"을 적는다.
        #   그래야 "이미 있는 행"을 알아본다.
        # excluded = 지금 INSERT 하려던 값 (excluded.rank = 새로 들어온 rank)
        cur.execute(
            """
            INSERT INTO product_snapshots
            (product_id, snapshot_date, rank, price, review_count)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(product_id, snapshot_date) DO UPDATE SET
                rank = excluded.rank,
                price = excluded.price,
                review_count = excluded.review_count
            """,
            (
                item["product_id"],
                snapshot_date,
                item["rank"],
                item["price"],
                item["review_count"],
            )
        )

    # ★커밋은 반복문이 다 끝난 뒤 한 번만.
    #   루프 안에서 커밋하면 중간 실패 시 "반만 저장된" 상태가 남는다.
    conn.commit()


# ---------------------------------------------------------
# 저장된 날짜 목록 (오래된 순)
# ---------------------------------------------------------
def get_snapshot_dates(conn) -> list[str]:
    cur = conn.cursor()

    rows = cur.execute(
        """
        SELECT DISTINCT snapshot_date
        FROM product_snapshots
        ORDER BY snapshot_date ASC
        """
    ).fetchall()

    return [row["snapshot_date"] for row in rows]


# ---------------------------------------------------------
# 특정 날짜 스냅샷 상세 조회
# ---------------------------------------------------------
# 이름은 products 에 있으므로 JOIN 한다.
# INNER JOIN 인 이유: 스냅샷은 항상 products 를 거쳐 만들어져서
#                    자식이 부모보다 먼저 생길 수 없다.
def get_snapshot_rows(conn, snapshot_date: str) -> list[dict]:
    cur = conn.cursor()

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

    # Row -> dict (FastAPI 가 JSON 으로 바꾸려면 dict 여야 한다)
    return [dict(row) for row in rows]


# ---------------------------------------------------------
# 스냅샷을 product_id 기준 dict 로 변환
# ---------------------------------------------------------
#   {"A100": {...}, "A200": {...}}
# compare_service 에서 두 날짜를 짝지을 때 O(1) 로 찾으려고 쓴다.
def get_snapshot_map(conn, snapshot_date: str) -> dict:
    items = get_snapshot_rows(conn, snapshot_date)
    return {item["product_id"]: item for item in items}
