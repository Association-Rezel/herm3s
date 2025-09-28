from pydantic import BaseModel


class PtahVersionResponse(BaseModel):
    message: str
    mac: str
    ptah_version_hash: str
    download_url: str
