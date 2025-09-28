from fastapi import APIRouter

from .config import router as config_router
from .ptah import router as ptah_router

router = APIRouter(prefix="/v2")
router.include_router(ptah_router)
router.include_router(config_router)
