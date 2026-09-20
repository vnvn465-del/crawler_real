# =========================
# run_pipeline.py
# 수집 파이프라인 실행용 스크립트
# =========================

# 종료 코드 전달용
import sys

# 예외 종류 구분용
import httpx

# 커스텀 예외
from app.crawler.parser import ParseError

# crawl service import
from app.services.crawl_service import collect_and_save_snapshot


def main() -> int:
    try:
        result = collect_and_save_snapshot()

    except ParseError as exc:
        print("[수집 실패] 페이지 구조가 바뀌었거나 요청이 차단된 것으로 보입니다.")
        print(f"  원인: {exc}")
        print("  → DB에는 아무것도 저장하지 않았습니다.")
        return 1

    except httpx.HTTPStatusError as exc:
        print(f"[수집 실패] 서버가 오류를 반환했습니다: HTTP {exc.response.status_code}")
        return 1

    except httpx.RequestError as exc:
        print(f"[수집 실패] 서버에 연결하지 못했습니다: {type(exc).__name__}")
        print("  → 수집 대상 서버가 켜져 있는지, 주소가 맞는지 확인하세요.")
        return 1

    print(f"[저장 완료] snapshot_date={result['snapshot_date']}")
    print(f"[저장 건수] {result['count']}개")
    print(f"[fetch 방식] {result['fetch_mode']}")

    print("\n[저장된 항목]")
    for item in result["items"]:
        print(item)

    if result["count"] == 0:
        print("[경고] 저장된 항목이 0건입니다. 성공으로 처리하지 않습니다.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
