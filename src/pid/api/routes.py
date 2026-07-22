from fastapi import APIRouter

from pid.api.routers import router as api_router

router = APIRouter()
router.include_router(api_router)
