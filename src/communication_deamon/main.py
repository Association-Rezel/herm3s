from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from MacAddress import MacAddress
from test_mainUser_configFile import create_main_user_config_file
 

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
        config_file = create_main_user_config_file(mac_box.getMac())
        return config_file
    else:
        raise HTTPException(404, {"Erreur": "invalid mac address"})
