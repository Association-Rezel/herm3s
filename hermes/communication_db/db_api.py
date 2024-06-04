"""
Provides an API to interact with the MongoDb database.
"""

# import requests
from pymongo import MongoClient

from env import DB_URI, DB_NAME
from .db_models import Box, UnetProfile, WanVlan


class DbApi:
    """Provides an API to interact with the MongoDb database."""

    def __init__(self) -> None:
        self.mongodb_client = MongoClient(DB_URI)
        self.db = self.mongodb_client[DB_NAME]
        self.db.boxes = self.db.hermestest1

    def test(self):
        """tests"""
        return self.db.boxes.find_one()

    def get_box_by_mac(self, mac: str) -> dict:
        """Get a box by its MAC address."""
        res = self.db.boxes.find_one({"mac": mac})
        box = Box(
            id=str(res["_id"]),
            type=res["type"],
            mac=res["mac"],
            unets=[UnetProfile(**unet) for unet in res["unets"]],
            wan_vlan=[WanVlan.model_validate_strings(wan_vlan) for wan_vlan in res["wan-vlan"]],
        )
        return box
