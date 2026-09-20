# =========================
# playwright_fetch.py
# 브라우저 기반으로 HTML을 가져오는 역할
# =========================

# Playwright sync API import
from playwright.sync_api import sync_playwright

# 설정값 import
from config import HEADLESS, WAIT_SELECTOR


# Playwright를 사용해서 페이지 HTML을 가져오는 함수
def fetch_html_with_playwright(url):
    # Playwright 실행 시작
    with sync_playwright() as p:
        # Chromium 브라우저 실행
        browser = p.chromium.launch(headless=HEADLESS)

        # 새 페이지 생성
        page = browser.new_page()

        # URL 접속
        # wait_until="networkidle"은 네트워크 요청이 거의 멈출 때까지 대기
        page.goto(url, wait_until="networkidle")

        # 필요한 경우 특정 요소가 나타날 때까지 대기
        if WAIT_SELECTOR:
            page.wait_for_selector(WAIT_SELECTOR, timeout=10000)

        # 최종 렌더링된 HTML 가져오기
        html = page.content()

        # 브라우저 종료
        browser.close()

        # HTML 문자열 반환
        return html
