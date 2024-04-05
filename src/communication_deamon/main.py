from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from MacAddress import MacAddress
 

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
    file = "test.txt"
    if mac_box.getMac() is not None:
        return FileResponse(file, filename=file)
    else:
        raise HTTPException(404, {"Erreur": "invalid mac address"})
