import os
import yaml
import json

config_file_exists = False
config = {"api": {}}
if "CONFIG_PATH" in os.environ and os.path.exists(os.environ["CONFIG_PATH"]):
    config_file_exists = True
    with open(os.environ["CONFIG_PATH"], "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

if "DEF_ROUTER_IP_VLAN" in os.environ:
    DEF_ROUTER_IP_VLAN = json.loads(os.environ["DEF_ROUTER_IP_VLAN"])
elif config_file_exists and "DEF_ROUTER_IP_VLAN" in config['api']:
    DEF_ROUTER_IP_VLAN = config['api']['DEF_ROUTER_IP_VLAN']
else:
    DEF_ROUTER_IP_VLAN = {101: "10.121.0.1", 102: "10.122.0.1"}

if "FILE_SAVING_PATH" in os.environ:
    FILE_SAVING_PATH = os.environ["FILE_SAVING_PATH"]
elif config_file_exists and "FILE_SAVING_PATH" in config['api']:
    FILE_SAVING_PATH = config['api']['FILE_SAVING_PATH']
else:
    FILE_SAVING_PATH = "/dev/shm/"
