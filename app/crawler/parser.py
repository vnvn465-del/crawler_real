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


# 문자열에서 숫자만 추출해 int로 변환하는 함수
def to_int(text: str) -> int:
    # 숫자가 아닌 문자 제거
    numbers = re.sub(r"[^0-9]", "", text)

    # 숫자가 있으면 int 변환, 없으면 0 반환
    return int(numbers) if numbers else 0


# HTML 문자열에서 상품 목록을 파싱하는 함수
def parse_products(html: str) -> list[dict]:
    # HTML을 BeautifulSoup 객체로 변환
    soup = BeautifulSoup(html, PARSER_ENGINE)

    # 결과 리스트
    items = []

    # 각 상품 요소 순회
    for product in soup.select("li.product"):
        # 상품 ID 추출
        product_id = product.get("data-id")

        # 필요한 요소 찾기
        rank_el = product.select_one(".rank")
        name_el = product.select_one(".name")
        price_el = product.select_one(".price")
        reviews_el = product.select_one(".reviews")

        # 하나라도 없으면 skip
        if not all([product_id, rank_el, name_el, price_el, reviews_el]):
            continue

        # 상품 데이터 정리
        item = {
            "product_id": product_id,
            "rank": to_int(rank_el.get_text(strip=True)),
            "name": name_el.get_text(strip=True),
            "price": to_int(price_el.get_text(strip=True)),
            "review_count": to_int(reviews_el.get_text(strip=True)),
        }

        # 결과에 추가
        items.append(item)

    return items
