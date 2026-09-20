# =========================
# pipeline.py
# 전체 실행 흐름 제어
# =========================

# 오늘 날짜를 구하기 위한 모듈
from datetime import date

# 설정값 import
from config import URL, DB_PATH, SNAPSHOT_DATE, FETCH_MODE

# fetch 방식별 함수 import
from fetcher import fetch_html
from playwright_fetch import fetch_html_with_playwright

# 기능별 모듈 import
from parser import parse_products
from storage import connect_db, create_tables, save_items, get_snapshot_by_date


# fetch 방식에 따라 HTML을 가져오는 함수
def get_html(url):
    # 일반 HTTP 요청 방식
    if FETCH_MODE == "httpx":
        return fetch_html(url)

    # 브라우저 렌더링 방식
    elif FETCH_MODE == "playwright":
        return fetch_html_with_playwright(url)

    # 잘못된 설정값 예외 처리
    else:
        raise ValueError(f"지원하지 않는 FETCH_MODE입니다: {FETCH_MODE}")


# 전체 파이프라인 실행 함수
def main():
    # 1) 설정된 fetch 방식으로 HTML 가져오기
    html = get_html(URL)

    # 2) HTML 파싱해서 상품 목록 추출
    items = parse_products(html)

    # 3) DB 연결
    conn = connect_db(DB_PATH)
    cur = conn.cursor()

    # 4) 테이블 생성
    create_tables(cur)

    # 5) 저장할 날짜 결정
    # config.py에 SNAPSHOT_DATE가 있으면 그 날짜 사용
    # 없으면 오늘 날짜 사용
    snapshot_date = SNAPSHOT_DATE if SNAPSHOT_DATE else date.today().isoformat()

    # 6) 상품 목록 저장
    save_items(cur, items, snapshot_date)

    # 7) DB 반영
    conn.commit()

    # 8) 저장 완료 메시지
    print(f"[저장 완료] snapshot_date={snapshot_date}")
    print(f"[저장 건수] {len(items)}개")
    print(f"[fetch 방식] {FETCH_MODE}")

    # 9) 해당 날짜에 저장된 데이터 조회
    print("\n[해당 날짜 저장된 스냅샷]")
    rows = get_snapshot_by_date(cur, snapshot_date)

    for row in rows:
        print(row)

    # 10) DB 연결 종료
    conn.close()


# 현재 파일을 직접 실행했을 때만 main() 실행
if __name__ == "__main__":
    main()
