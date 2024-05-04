import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware


# sys.path.append("communication_deamon")
# sys.path.append("communication_netbox")
# sys.path.append("hermes_config_buildind")


from .MacAddress import MacAddress
from .creation_configfile import create_configfile, create_default_configfile


app = FastAPI()

# Enable CORS (for swagger)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        create_configfile(mac_box)
        return FileResponse(
            "{Config.default_path_files_saving}configfile_" + mac_box + ".txt",
            filename="configfile.txt",
        )
    else:
        raise HTTPException(404, {"Erreur": "invalid mac address"})


# download default conf file
@app.get("/v1/config/ac2350/default/file")
async def get_default_config():
    """
    Download the default configuration file
    """
    create_default_configfile()
    return FileResponse(
        "{Config.default_path_files_saving}defaultConfigfile.txt",
        filename="defaultConfigfile.txt",
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
