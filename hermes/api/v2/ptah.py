from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
import requests

from hermes.api.dependencies import (
    check_mac_matches_payload,
    get_credentials,
)
from hermes.api.models import PtahVersionResponse
from hermes.mongodb.db import get_box_by_mac, get_db
from hermes.env import ENV
from common_models.base import validate_mac

router = APIRouter(prefix="/ptah", dependencies=[Depends(check_mac_matches_payload)])


@router.get("/version/{mac}")
async def get_ptah_version(
    mac: str,
    credentials: Annotated[str, Depends(get_credentials)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    """
    Get the Ptah version for a specific MAC address.
    """
    mac_box = validate_mac(mac)

    box = await get_box_by_mac(db, mac_box)

    ptah_prepare_url = f"{ENV.ptah_base_url}/v1/build/prepare/{str(mac_box)}"
    response = requests.post(
        ptah_prepare_url,
        headers={"Authorization": f"Bearer {credentials}"},
        json={"profile": box.ptah_profile},
    )
    response.raise_for_status()

    ptah_response = PtahVersionResponse.model_validate_json(response.content)

    return JSONResponse(
        content={
            "version": ptah_response.ptah_version_hash,
        },
    )


@router.get("/download/{mac}")
async def get_ptah_download(
    mac: str,
    credentials: Annotated[str, Depends(get_credentials)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    """
    Download and stream the file associated with the given MAC address.
    """
    mac_box = validate_mac(mac)
    try:
        box = await get_box_by_mac(db, mac_box)
    except ValueError as e:
        return JSONResponse(status_code=404, content={"detail": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

    ptah_prepare_url = f"{ENV.ptah_base_url}/v1/build/prepare/{str(mac_box)}"
    response = requests.post(
        ptah_prepare_url,
        headers={"Authorization": f"Bearer {credentials}"},
        json={"profile": box.ptah_profile},
        timeout=180,
    )
    response.raise_for_status()

    ptah_download_url = f"{ENV.ptah_base_url}/v1/build/{str(mac_box)}"
    response = requests.post(
        ptah_download_url,
        headers={"Authorization": f"Bearer {credentials}"},
        stream=True,
        timeout=180,
    )

    response.raise_for_status()

    filename = "ptah.bin"

    return StreamingResponse(
        response.iter_content(chunk_size=8192),
        media_type=response.headers.get("Content-Type", "application/octet-stream"),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
