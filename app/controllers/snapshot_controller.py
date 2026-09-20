# =========================
# app/controllers/snapshot_controller.py
# 스냅샷 조회 API
# =========================

# FastAPI 모듈 import
from fastapi import APIRouter, HTTPException

# service import
from app.services.snapshot_service import (
    list_snapshot_dates,
    get_snapshot_by_date,
    get_latest_snapshot,
)


# router 생성
router = APIRouter(prefix="/snapshots", tags=["snapshots"])


# 저장된 날짜 목록 조회
@router.get("/dates")
def read_snapshot_dates():
    return {"dates": list_snapshot_dates()}


# 최신 스냅샷 조회
@router.get("/latest")
def read_latest_snapshot():
    # service 호출
    result = get_latest_snapshot()

    # 데이터가 없으면 404
    if result is None:
        raise HTTPException(status_code=404, detail="저장된 스냅샷이 없습니다.")

    return result


# 특정 날짜 스냅샷 조회
@router.get("/date/{snapshot_date}")
def read_snapshot_by_date(snapshot_date: str):
    # service 호출
    result = get_snapshot_by_date(snapshot_date)

    # 데이터가 없으면 404
    if result is None:
        raise HTTPException(status_code=404, detail="해당 날짜 스냅샷이 없습니다.")

    return result
