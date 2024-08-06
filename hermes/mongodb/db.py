import logging
from typing import Optional

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from netaddr import EUI

from hermes.env import ENV
from hermes.mongodb.models import Box

database: Optional[AsyncIOMotorDatabase] = None
db_client: Optional[AsyncIOMotorClient] = None


@Depends
def get_db() -> AsyncIOMotorDatabase:
    if database is None:
        raise ValueError("Database is not connected.")

    return database


def init_db():
    logging.info("Connecting to mongo...")
    global database, db_client
    db_client = AsyncIOMotorClient(ENV.db_uri)
    database = db_client.get_database(ENV.db_name)
    logging.info("Connected to mongo.")


def close_db():
    logging.info("Closing connection to mongo...")
    global db_client
    if db_client is not None:
        db_client.close()
    logging.info("Mongo connection closed.")


async def get_box_by_mac(db: AsyncIOMotorDatabase, mac: EUI) -> Box:
    """Get a box by its MAC address."""
    res = await db.boxes.find_one({"mac": str(mac)})
    if res is None:
        raise ValueError(f"Box with MAC address {str(mac)} not found")
    res["_id"] = str(res["_id"])
    box = Box.model_validate(res)
    return box
