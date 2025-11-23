import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hermes.env import ENV
from hermes.mongodb.db import close_db, init_db
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


if __name__ == "__main__":
    uvicorn.run("hermes.main:app", host="::", reload=True)
