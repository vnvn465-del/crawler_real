# =========================
# app/core/config.py
# 프로젝트 공통 설정값
# =========================

# 수집 대상 URL
# 지금은 로컬 html 서버를 사용
TARGET_URL = "http://127.0.0.1:8000/ranking_js.html"

# SQLite DB 파일 경로
DB_PATH = "crawler.db"

# HTTP 요청 타임아웃(초)
REQUEST_TIMEOUT = 10.0

# BeautifulSoup 파서 엔진
PARSER_ENGINE = "lxml"

# fetch 방식
# "httpx" 또는 "playwright"
FETCH_MODE = "playwright"

# Playwright 설정
HEADLESS = True
WAIT_SELECTOR = "li.product"

# 테스트용 날짜
# None이면 오늘 날짜 사용
SNAPSHOT_DATE = None
