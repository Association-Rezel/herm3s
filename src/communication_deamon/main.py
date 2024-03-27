from netaddr import EUI
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi import HTTPException

#class to check if the mac address is valid and store it
class MacAddress:
    mac : str = None;
    def __init__(self, mac:str):
        try:
            self.mac = str(EUI(mac)).replace("-", ":")
        except Exception as e:
            None 
    def getMac(self):
        return self.mac


app = FastAPI()

#download file from hermes to box
@app.get("/box/{mac}/config",)

async def get_file_config_init(mac: str):
    mac_box = MacAddress(mac)
    file = "spécification.txt"
    if not mac_box.getMac() is None:
        return FileResponse(file, filename=file)
    else:
        raise HTTPException(404, {"Erreur": "MAC invalide."}) 
    