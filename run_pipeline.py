# =========================
# run_pipeline.py
# 수집 파이프라인 실행용 스크립트
# =========================

# crawl service import
from app.services.crawl_service import collect_and_save_snapshot


# 메인 실행 함수
def main():
    # 수집 + 저장 실행
    result = collect_and_save_snapshot()

    # 저장 결과 출력
    print(f"[저장 완료] snapshot_date={result['snapshot_date']}")
    print(f"[저장 건수] {result['count']}개")
    print(f"[fetch 방식] {result['fetch_mode']}")

    print("\n[저장된 항목]")
    for item in result["items"]:
        print(item)


# 직접 실행 시 main() 호출
if __name__ == "__main__":
    main()
