from fastapi import APIRouter
from .config_ac2350 import router as config_ac2350_router
from .sysupgrade import router as sysupgrade_router

router = APIRouter()

router.include_router(config_ac2350_router)
router.include_router(sysupgrade_router)


@router.get("/")
async def root():
    """
    Return 200 code
    """
    return {"status": "OK"}


@router.get("/status")
async def status():
    """
    Return 200 code
    """
    return {"status": "OK"}
