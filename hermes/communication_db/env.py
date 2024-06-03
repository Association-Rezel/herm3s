"""
"""

import os
import yaml

CONFIG_FILE_EXISTS = False
config = {"communication_db": {}}
if "CONFIG_PATH" in os.environ and os.path.exists(os.environ["CONFIG_PATH"]):
    CONFIG_FILE_EXISTS = True
    with open(os.environ["CONFIG_PATH"], "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

if "DB_URI" in os.environ:
    DB_URI = os.environ["TOKEN_NETBOX"]
elif CONFIG_FILE_EXISTS and "TOKEN_NETBOX" in config["communication_netbox"]:
    DB_URI = config["communication_netbox"]["TOKEN_NETBOX"]
else:
    DB_URI = "mongodb://admintest:Rwy4ygL5hqoNUr@137.194.13.162/?retryWrites=true&w=majority&authSource=test"

if "DB_NAME" in os.environ:
    DB_NAME = os.environ["URL_NETBOX"]
elif CONFIG_FILE_EXISTS and "URL_NETBOX" in config["communication_netbox"]:
    DB_NAME = config["communication_netbox"]["URL_NETBOX"]
else:
    DB_NAME = "test"
