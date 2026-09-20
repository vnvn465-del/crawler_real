# =========================
# app/controllers/health_controller.py
# 헬스체크 / 루트 엔드포인트
# =========================

# APIRouter import
from fastapi import APIRouter


# router 생성
router = APIRouter(tags=["health"])


# 서버 상태 확인용 엔드포인트
@router.get("/")
def read_root():
    return {"message": "Crawler API is running"}
