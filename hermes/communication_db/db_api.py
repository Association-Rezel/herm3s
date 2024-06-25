"""
Provides an API to interact with the MongoDB database.
"""

from pymongo import MongoClient

from .env import DB_URI, DB_NAME
from .db_models import Box, UnetProfile, WanVlan


class DbApi:
    """Provides an API to interact with the MongoDB database."""

    def __init__(self) -> None:
        print(f"{DB_URI=} ; {DB_NAME=}")
        self.mongodb_client = MongoClient(DB_URI)
        self.db = self.mongodb_client[DB_NAME]
        self.db.boxes = self.db.boxes  # Collection name: boxes

    def get_box_by_mac(self, mac: str) -> Box:
        """Get a box by its MAC address."""
        res = self.db.boxes.find_one({"mac": mac})
        if res is None:
            raise ValueError(f"Box with MAC address {mac} not found")
        res["_id"] = str(res["_id"])
        box = Box.model_validate(res)
        return box
