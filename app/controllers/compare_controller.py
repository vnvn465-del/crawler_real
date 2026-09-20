# =========================
# app/controllers/compare_controller.py
# 날짜 비교 API
# =========================

# FastAPI 모듈 import
from fastapi import APIRouter, HTTPException

# service import
from app.services.compare_service import compare_latest_snapshots, compare_two_snapshots


# router 생성
router = APIRouter(prefix="/compare", tags=["compare"])


# 최신 2개 날짜 비교
@router.get("/latest")
def read_latest_compare():
    # service 호출
    result = compare_latest_snapshots()

    # 비교할 데이터가 부족하면 400
    if result is None:
        raise HTTPException(status_code=400, detail="비교할 날짜가 2개 이상 필요합니다.")

    return result


# 특정 두 날짜 비교
@router.get("/{old_date}/{new_date}")
def read_compare_between_dates(old_date: str, new_date: str):
    # service 호출
    result = compare_two_snapshots(old_date, new_date)

    # 해당 날짜 데이터가 없으면 404
    if result is None:
        raise HTTPException(status_code=404, detail="비교할 날짜 데이터가 없습니다.")

    return result
