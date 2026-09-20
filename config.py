# =========================
# config.py
# 프로젝트 전체 설정 파일
# =========================

# 테스트 대상 URL
URL = "http://127.0.0.1:8000/ranking.html"

# SQLite DB 파일명
DB_PATH = "crawler.db"

# HTTP 요청 타임아웃(초)
REQUEST_TIMEOUT = 10.0

# BeautifulSoup에서 사용할 파서 엔진
PARSER_ENGINE = "lxml"

# 테스트용 스냅샷 날짜
# None이면 오늘 날짜 사용
SNAPSHOT_DATE = "2026-09-21"

# fetch 방식 선택
# "httpx" 또는 "playwright"
FETCH_MODE = "httpx"

# Playwright 관련 설정
HEADLESS = True

# Playwright에서 페이지 로딩 후 기다릴 CSS selector
# 상품 목록이 나타날 때까지 기다리기 위해 사용
WAIT_SELECTOR = "li.product"
