"""
Bulk validation of all boxes in the mongodb db

Usage: python -m hermes.communication_db.scripts_model_validation.bulk_validation
"""

import pymongo

from ..db_models import Box

# GLOBALS
DB_URI = "mongodb://admintest:Rwy4ygL5hqoNUr@137.194.13.162/?retryWrites=true&w=majority&authSource=test"
DB_NAME = "test"


mongo_client = pymongo.MongoClient(DB_URI)
db = mongo_client[DB_NAME]
boxes = db.hermestest1

nb_valid = 0
nb_total = 0
for box in boxes.find():
    print(f"\n--- Validating box {box['mac']} ---")
    del box["_id"]
    try:
        Box.model_validate(box)
    except Exception as e:
        print(f"Error validating box {box['mac']}: {e}")
    else:
        print(f"Box {box['mac']} is valid")
        nb_valid += 1
    nb_total += 1
    print()

print(f"\n{nb_valid} boxes out of {nb_total} are valid.")
