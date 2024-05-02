import uvicorn
import sys
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware


# sys.path.append("communication_deamon")
# sys.path.append("communication_netbox")
# sys.path.append("hermes_config_buildind")


from hermes.src.communication_deamon.MacAddress import MacAddress
from hermes.src.communication_deamon.creation_configfile import create_configfile,create_default_configfile


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
        return FileResponse("/hermes/config_files/configfile.txt", filename="configfile.txt")
    else:
        raise HTTPException(404, {"Erreur": "invalid mac address"})

#download default conf file   
@app.get("/default/config")
async def get_default_config():
    create_default_configfile()
    return FileResponse("/hermes/config_files/defaultConfigfile.txt", filename="defaultConfigfile.txt")


if __name__ == "__main__" :
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
