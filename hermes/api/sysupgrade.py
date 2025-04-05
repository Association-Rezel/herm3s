from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import requests
from hermes.env import ENV

router = APIRouter()


@router.get("/v1/sysupgrade/{box}/{version}")
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


@router.get("/v1/ptah/latest-version")
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
