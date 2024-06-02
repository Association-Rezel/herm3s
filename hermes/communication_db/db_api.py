"""
Provides an API to interact with the MongoDb database.
"""

# import requests
from pymongo import MongoClient

from .env import DB_URI, DB_NAME


class DbApi :
    """Provides an API to interact with the MongoDb database."""

    def __init__(self) -> None:
        self.mongodb_client = MongoClient(DB_URI)
        self.db = self.mongodb_client[DB_NAME]

    def get_box_by_mac(self, mac: str) -> dict:
        """Get a box by its MAC address."""
        return self.db.boxes.find_one({"mac": mac})
