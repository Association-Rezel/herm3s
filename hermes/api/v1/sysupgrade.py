# This allows a smooth transition from API without mTLS. Clients will be able to uprade event if they don't have mTLS

from typing import Annotated
from fastapi import APIRouter, Depends, Request, HTTPException
import ipaddress

from fastapi.responses import JSONResponse, StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import HttpUrl
import requests
from hermes.api.dependencies import get_credentials
from hermes.env import ENV

from common_models.base import validate_mac

from hermes.mongodb.db import get_box_by_mac, get_db
from hermes.utils.K8sVaultTokenProcessing import K8sVaultTokenProcessing
from rezel_vault_jwt.jwt_transit_manager import JwtTransitManager

router = APIRouter()


def extract_mac_from_ipv6(ipv6: str) -> str | None:
    try:
        addr = ipaddress.IPv6Address(ipv6)
        interface_id = addr.packed[-8:]
        if interface_id[3] != 0xFF or interface_id[4] != 0xFE:
            return None
        mac_bytes = bytearray(interface_id[0:3] + interface_id[5:8])
        mac_bytes[0] ^= 0b00000010
        mac = ":".join(f"{b:02x}" for b in mac_bytes)
        return mac
    except Exception:
        return None


@router.get("/sysupgrade/{box}/{version}")
async def sysupgrade_to_version(
    request: Request,
    box: str,
    version: str,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    client_ip = request.headers.get("X-Forwarded-For", request.client.host)

    if not (mac := extract_mac_from_ipv6(client_ip)):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid IPv6 address",
                "message": "Unable to extract MAC address from the provided IPv6 address.",
            },
        )
    mac_box = validate_mac(mac)
    print(f"Extracted MAC address: {str(mac_box)}")
    try:
        box_obj = await get_box_by_mac(db, mac_box)
    except ValueError as e:
        return JSONResponse(status_code=404, content={"detail": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

    if not box_obj.ptah_profile == "ac2350-canary":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Unsupported profile",
                "message": "Sysupgrade is only supported for ac2350-canary profile.",
            },
        )

    k8s_token_processing = K8sVaultTokenProcessing(
        vault_url=ENV.vault_url,
        vault_role_name=ENV.vault_role_name,
    )

    vault_token = k8s_token_processing.get_vault_token()

    jwt_manager = JwtTransitManager(
        vault_token=vault_token,
        vault_base_url=HttpUrl(ENV.vault_url),
        transit_mount=ENV.vault_transit_mount,
        transit_key=ENV.vault_transit_key,
    )
    credentials = jwt_manager.issue_jwt({"mac": str(mac_box)})

    ptah_prepare_url = f"{ENV.ptah_base_url}/v1/build/prepare/{str(mac_box)}"
    response = requests.post(
        ptah_prepare_url,
        headers={"Authorization": f"Bearer {credentials}"},
        json={"profile": box_obj.ptah_profile},
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


@router.get("/ptah/latest-version")
async def get_latest_version():
    """
    Tell what is the latest version of the ptah firmware for the box
    """
    return {"version": "5.0.0"}
