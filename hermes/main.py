import logging

import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from netaddr import EUI, AddrFormatError, mac_unix_expanded

from hermes.env import ENV
from hermes.mongodb.db import close_db, get_box_by_mac, get_db, init_db
from hermes.api.routes import router as api_router

app = FastAPI()

# Enable CORS (for swagger)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_event_handler("startup", init_db)
app.add_event_handler("shutdown", close_db)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="::", reload=True)
