from netaddr import EUI
from fastapi import FastAPI
from fastapi.responses import FileResponse

#put into other file
from re import match
from fastapi import HTTPException


app = FastAPI()

#put into other file
def is_mac(mac:str):
    standard_mac=r'([a-fA-F0-9]{2}([:-][a-fA-F0-9]{2}){5})'
    if match(standard_mac,mac):
        return True
    return False
class MacAddress1:
    mac = None
    def __init__(self, mac:str):
        standard_mac = r'([a-fA-F0-9]{2}([:-][a-fA-F0-9]{2}){5})'
        if match(standard_mac,mac):
            self.mac = mac
        else:
            raise HTTPException(400, {"Erreur": "MAC invalide."})
        
    def getMac(self):
        return self.mac

class MacAddress:
    mac = None
    def __init__(self, mac:str):
        try:
            self.mac = str(EUI(mac)).replace("-", ":")
        except Exception as e:
            None 
    def getMac(self):
        return self.mac

#download file from server to client
@app.get("/box/{mac}/config",)

async def get_file_config_init(mac: str):
    mac_box = MacAddress(mac)
    file = "spécification.txt"
    print(mac_box.getMac())
    if not mac_box.getMac() is None:
        return FileResponse(file, filename=file)
    else:
        raise HTTPException(404, {"Erreur": "MAC invalide."}) 
    