from fastapi import APIRouter

from .sysupgrade import router as sysupgrade_router
from .config_ac2350 import router as config_ac2350_router

router = APIRouter(prefix="/v1")
router.include_router(sysupgrade_router)
router.include_router(config_ac2350_router)
