import logging

import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from netaddr import EUI, AddrFormatError, mac_unix_expanded

from hermes.api.config import ac2350 as config_ac2350
from hermes.env import ENV
from hermes.mongodb.db import close_db, get_box_by_mac, get_db, init_db

app = FastAPI()

# Enable CORS (for swagger)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_event_handler("startup", init_db)
app.add_event_handler("shutdown", close_db)


@app.get("/")
async def root():
    """
    Return 200 code
    """
    return {"status": "OK"}


@app.get("/status")
async def status():
    """
    Return 200 code
    """
    return {"status": "OK"}


# download file from hermes to box
@app.get("/v1/config/ac2350/{mac}")
async def ac2350_get_file_config_init(mac: str, db=get_db):
    """
    Download the configuration file for the box with the mac address mac
    args:
        mac: str: mac address of the box
    """
    try:
        mac_box = EUI(mac)
        mac_box.dialect = mac_unix_expanded
    except AddrFormatError as e:
        raise HTTPException(
            400, {"Erreur": "invalid mac address", "details": str(e)}
        ) from e
    try:
        config_ac2350.create_configfile(await get_box_by_mac(db, mac_box))
    except ValueError as e:
        logging.error("Error: %s", str(e))
        raise HTTPException(404, {"Erreur": str(e)}) from e
    return FileResponse(
        f"{ENV.temp_generated_box_configs_dir}configfile_" + str(mac_box) + ".txt",
        filename="configfile.txt",
    )


@app.get("/v1/config/ac2350/default/file")
async def ac2350_get_default_config():
    """
    Download the default configuration file
    """
    config_ac2350.create_default_configfile()
    return FileResponse(
        f"{ENV.temp_generated_box_configs_dir}defaultConfigfile.txt",
        filename="defaultConfigfile.txt",
    )


@app.get("/v1/sysupgrade/{box}/{version}")
async def sysupgrade_to_version(box: str, version: str):
    """
    Download the default configuration file
    """
    if version == "latest":
        url = f"{ENV.ptah_releases_base_url}/permalink/latest/downloads/bin/openwrt-ptah-{box}.bin"
    else:
        url = f"{ENV.ptah_releases_base_url}{version}/downloads/bin/openwrt-ptah-{box}.bin"
    headers = {"PRIVATE-TOKEN": ENV.gitlab_ptah_access_token}
    try:
        response = requests.get(url, stream=True, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        raise HTTPException(500, {"Erreur": str(e)}) from e
    if response.status_code == 404:
        raise HTTPException(
            response.status_code, {"Erreur": "version not found on gitlab"}
        )
    elif response.status_code == 401:
        raise HTTPException(
            response.status_code,
            {
                "Erreur": "unauthorized access to gitlab (maybe PTAH_ACCESS_TOKEN is missing or expired)"
            },
        )
    elif response.status_code != 200:
        raise HTTPException(
            response.status_code, {"Erreur": "unable to retrieve file from gitlab"}
        )

    def iter_content(response: requests.Response):
        for chunk in response.iter_content(chunk_size=8192):
            yield chunk

    return StreamingResponse(
        iter_content(response),
        headers={"Content-Disposition": "attachment; filename=sysupgrade.bin"},
    )


@app.get("/v1/ptah/latest-version")
async def get_latest_version():
    """
    Tell what is the latest version of the ptah firmware for the box
    """
    url = f"{ENV.ptah_releases_base_url}/permalink/latest"
    headers = {"PRIVATE-TOKEN": ENV.gitlab_ptah_access_token}
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        raise HTTPException(500, {"Erreur": str(e)}) from e
    if response.status_code == 401:
        raise HTTPException(
            500,
            {
                "Erreur": "unauthorized access to gitlab (maybe PTAH_ACCESS_TOKEN is missing or expired)"
            },
        )
    elif response.status_code != 200:
        raise HTTPException(500, {"Erreur": "unable to get latest version from gitlab"})

    version = response.json()["tag_name"]

    return {"version": version}


if __name__ == "__main__":
    uvicorn.run("main:app", host="::", reload=True)
