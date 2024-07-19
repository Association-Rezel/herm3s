from netaddr import EUI, mac_unix_expanded, AddrFormatError
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .api.config import ac2350 as config_ac2350
import requests
from . import config

app = FastAPI()

# Enable CORS (for swagger)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
async def ac2350_get_file_config_init(mac: str):
    """
    Download the configuration file for the box with the mac address mac
    args:
        mac: str: mac address of the box
    """
    try:
        mac_box = EUI(mac)
        mac_box.dialect = mac_unix_expanded
    except AddrFormatError:
        raise HTTPException(400, {"Erreur": "invalid mac address"})
    try:
        config_ac2350.create_configfile(mac_box)
    except ValueError as e:
        raise HTTPException(404, {"Erreur": str(e)})
    return FileResponse(
        f"{config.FILE_SAVING_PATH}configfile_" + str(mac_box) + ".txt",
        filename="configfile.txt",
    )


@app.get("/v1/config/ac2350/default/file")
async def ac2350_get_default_config():
    """
    Download the default configuration file
    """
    config_ac2350.create_default_configfile()
    return FileResponse(
        f"{config.FILE_SAVING_PATH}defaultConfigfile.txt",
        filename="defaultConfigfile.txt",
    )


@app.get("/v1/sysupgrade/{box}/{version}")
async def sysupgrade(box: str, version: str):
    """
    Download the default configuration file
    """
    if version == "latest":
        url = f"{config.GITLAB_BASE_URL}/permalink/latest/downloads/bin/openwrt-ptah-{box}.bin"
    else:
        url = f"{config.GITLAB_BASE_URL}{version}/downloads/bin/openwrt-ptah-{box}.bin"
    headers = {"PRIVATE-TOKEN": config.PTAH_ACCESS_TOKEN}
    try:
        response = requests.get(url, stream=True, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        raise HTTPException(500, {"Erreur": str(e)})
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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
