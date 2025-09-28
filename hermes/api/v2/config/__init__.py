import logging
from typing import Annotated
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import APIRouter, Depends, HTTPException

from hermes.api.dependencies import jwt_required
from hermes.env import ENV
from hermes.mongodb.db import get_box_by_mac, get_db
from common_models.base import validate_mac

router = APIRouter(prefix="/config", dependencies=[Depends(jwt_required)])


@router.get("/{mac}")
async def get_file_config_by_mac(
    mac: str, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
):
    """
    Download the configuration file for the box with the mac address mac
    args:
        mac: str: mac address of the box
    """
    mac_box = validate_mac(mac)
    box = await get_box_by_mac(db, mac_box)
    if box is None:
        raise HTTPException(404, {"Erreur": f"Box with mac {str(mac_box)}not found"})

    match box.type:
        case "ac2350":
            from hermes.api.v2.config.ac2350 import create_configfile
        case _:
            raise HTTPException(400, {"Erreur": f"Box type {box.type} not supported"})
    try:
        create_configfile(box)
    except ValueError as e:
        logging.error("Error: %s", str(e))
        raise HTTPException(404, {"Erreur": str(e)}) from e
    return FileResponse(
        f"{ENV.temp_generated_box_configs_dir}configfile_" + str(mac_box) + ".txt",
        filename="configfile.txt",
    )


@router.get("/{mac}/default")
async def get_default_config_by_mac(
    mac: str, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
):
    """
    Download the default configuration file
    """
    mac_box = validate_mac(mac)
    box = await get_box_by_mac(db, mac_box)
    if box is None:
        raise HTTPException(404, {"Erreur": f"Box with mac {str(mac_box)}not found"})
    match box.type:
        case "ac2350":
            from hermes.api.v2.config.ac2350 import create_default_configfile
        case _:
            raise HTTPException(400, {"Erreur": f"Box type {box.type} not supported"})
    create_default_configfile()
    return FileResponse(
        f"{ENV.temp_generated_box_configs_dir}{box.type}_defaultConfigfile.txt",
        filename="defaultConfigfile.txt",
    )
