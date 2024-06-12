import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .api.MacAddress import MacAddress
from .api.config import ac2350
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
async def get_file_config_init(mac: str):
    """
    Download the configuration file for the box with the mac address mac
    args:
        mac: str: mac address of the box
    """
    mac_box = MacAddress(mac).getMac()
    if mac_box is not None:
        try:
            ac2350.create_configfile(mac_box)
        except ValueError as e:
            raise HTTPException(404, {"Erreur": str(e)})
        return FileResponse(
            f"{config.FILE_SAVING_PATH}configfile_" + mac_box + ".txt",
            filename="configfile.txt",
        )
    else:
        raise HTTPException(400, {"Erreur": "invalid mac address"})


@app.get("/v1/config/ac2350/default/file")
async def get_default_config():
    """
    Download the default configuration file
    """
    ac2350.create_default_configfile()
    return FileResponse(
        f"{config.FILE_SAVING_PATH}defaultConfigfile.txt",
        filename="defaultConfigfile.txt",
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
