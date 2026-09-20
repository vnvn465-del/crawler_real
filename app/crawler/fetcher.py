# =========================
# app/crawler/fetcher.py
# 일반 HTTP 요청 기반 HTML 수집
# =========================

# HTTP 요청 라이브러리 import
import httpx

# 설정값 import
from app.core.config import REQUEST_TIMEOUT


# URL에서 HTML을 가져오는 함수
def fetch_html(url: str) -> str:
    # GET 요청 전송
    response = httpx.get(url, timeout=REQUEST_TIMEOUT)

    # 200번대 응답이 아니면 예외 발생
    response.raise_for_status()

    # HTML 문자열 반환
    return response.text
