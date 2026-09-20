# =========================
# app/crawler/parser.py
# HTML에서 상품 데이터 추출
# =========================

# 정규표현식 모듈
import re

# BeautifulSoup import
from bs4 import BeautifulSoup

# 설정 import
from app.core.config import PARSER_ENGINE

# 필드 누락률 허용 한계
# 30%를 넘으면 "구조가 바뀌었다"고 판단하고 수집을 중단한다.
MAX_MISSING_RATE = 0.3

# 데이터를 믿을 수 없는 상태를 나타내는 전용 예외
class ParseError(RuntimeError):
    """신뢰할 수 있는 데이터를 만들 수 없는 상태."""


# 문자열에서 숫자만 추출해 int로 변환하는 함수
# 숫자가 없으면 None(파싱 실패)을 반환한다. 0으로 둔갑시키지 않는다.
def to_int(text: str | None) -> int | None:
    # None이 들어와도 안전하게 빈 문자열로 처리
    numbers = re.sub(r"[^0-9]", "", text or "")

    # 숫자가 있으면 int, 없으면 None
    return int(numbers) if numbers else None


# HTML 문자열에서 상품 목록을 파싱하는 함수
def parse_products(html: str) -> list[dict]:
    # HTML을 BeautifulSoup 객체로 변환
    soup = BeautifulSoup(html, PARSER_ENGINE)

    # 상품 요소 전체 조회  (① 순회가 아니라 먼저 목록으로 받는다)
    nodes = soup.select("li.product")

    # (1) 노드가 0개면 빈 리스트를 돌려주지 않고 실패시킨다
    if not nodes:
        raise ParseError(
            "상품 노드가 0개입니다. item 셀렉터('li.product')가 더 이상 맞지 않거나 "
            f"요청이 차단되었을 수 있습니다. (응답 길이 {len(html)}자)"
        )

    items: list[dict] = []

    # ② 건너뛴 항목 수 (누락률 계산용)
    skipped = 0

    for product in nodes:
        product_id = product.get("data-id")

        rank_el = product.select_one(".rank")
        name_el = product.select_one(".name")
        price_el = product.select_one(".price")
        reviews_el = product.select_one(".reviews")

        # ③ 요소가 하나라도 없으면 건너뛰고 센다
        if not all([product_id, rank_el, name_el, price_el, reviews_el]):
            skipped += 1
            continue

        rank = to_int(rank_el.get_text(strip=True))
        price = to_int(price_el.get_text(strip=True))
        review_count = to_int(reviews_el.get_text(strip=True))

        # (2) ④ 요소는 있는데 값이 숫자가 아닌 경우도 실패로 본다
        #     (예: 순위가 "품절", 가격이 "-")
        if rank is None or price is None:
            skipped += 1
            continue

        items.append({
            "product_id": product_id,
            "rank": rank,
            "name": name_el.get_text(strip=True),
            "price": price,
            "review_count": review_count,   # ⑤ 리뷰 수는 없을 수 있으므로 None 허용
        })

    # (3) ⑥ 일부만 빠진 경우도 누락률로 판단한다
    missing_rate = skipped / len(nodes)
    if missing_rate > MAX_MISSING_RATE:
        raise ParseError(
            f"필드 누락률이 {missing_rate:.0%} 입니다 "
            f"(노드 {len(nodes)}개 중 {skipped}개 실패). 페이지 구조 변경을 의심하세요."
        )

    return items

