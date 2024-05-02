from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from communication_deamon.MacAddress import MacAddress
from communication_deamon.creation_configfile import create_configfile


app = FastAPI()

# Enable CORS (for swagger)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#download file from hermes to box
@app.get("/box/{mac}/config",)
async def get_file_config_init(mac: str):
    mac_box = MacAddress(mac)
    if mac_box.getMac() is not None:
        create_configfile(mac_box.getMac())
        return FileResponse("configfile.txt", filename="configfile.txt")
    else:
        raise HTTPException(404, {"Erreur": "invalid mac address"})

#download default conf file   
@app.get("/default/config")
async def get_default_config():
    return FileResponse("defaultConfigfile.txt", filename="defaultConfigfile.txt")
