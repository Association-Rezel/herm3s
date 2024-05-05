import os
import yaml

config_file_exists = False
config = {"communication_netbox": {}}
if "CONFIG_PATH" in os.environ and os.path.exists(os.environ["CONFIG_PATH"]):
    config_file_exists = True
    with open(os.environ["CONFIG_PATH"], "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

if "TOKEN_NETBOX" in os.environ:
    TOKEN_NETBOX = os.environ["TOKEN_NETBOX"]
elif config_file_exists and "TOKEN_NETBOX" in config["communication_netbox"]:
    TOKEN_NETBOX = config["communication_netbox"]["TOKEN_NETBOX"]
else:
    TOKEN_NETBOX = "default_token"

if "URL_NETBOX" in os.environ:
    URL_NETBOX = os.environ["URL_NETBOX"]
elif config_file_exists and "URL_NETBOX" in config["communication_netbox"]:
    URL_NETBOX = config["communication_netbox"]["URL_NETBOX"]
else:
    URL_NETBOX = "http://netbox:8000"
