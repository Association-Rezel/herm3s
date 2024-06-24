import os
import yaml
import json

config_file_exists = False
config = {"api": {}}
if "CONFIG_PATH" in os.environ and os.path.exists(os.environ["CONFIG_PATH"]):
    config_file_exists = True
    with open(os.environ["CONFIG_PATH"], "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

if "DNS_SERVERS" in os.environ:
    DNS_SERVERS = json.loads(os.environ["DNS_SERVERS"])
elif config_file_exists and "DNS_SERVERS" in config["api"]:
    DNS_SERVERS = config["api"]["DNS_SERVERS"]
else:
    DNS_SERVERS = ["8.8.8.8", "8.8.4.4"]

if "FILE_SAVING_PATH" in os.environ:
    FILE_SAVING_PATH = os.environ["FILE_SAVING_PATH"]
elif config_file_exists and "FILE_SAVING_PATH" in config["api"]:
    FILE_SAVING_PATH = config["api"]["FILE_SAVING_PATH"]
else:
    FILE_SAVING_PATH = "/dev/shm/"

if "PTAH_ACCESS_TOKEN" in os.environ:
    PTAH_ACCESS_TOKEN = os.environ["PTAH_ACCESS_TOKEN"]
elif config_file_exists and "PTAH_ACCESS_TOKEN" in config["api"]:
    PTAH_ACCESS_TOKEN = config["api"]["PTAH_ACCESS_TOKEN"]
else:
    PTAH_ACCESS_TOKEN = "notset"

if "GITLAB_BASE_URL" in os.environ:
    GITLAB_BASE_URL = os.environ["GITLAB_BASE_URL"]
elif config_file_exists and "GITLAB_BASE_URL" in config["api"]:
    GITLAB_BASE_URL = config["api"]["GITLAB_BASE_URL"]
else:
    GITLAB_BASE_URL = "https://gitlab.fai.rezel.net/api/v4/projects/15/releases/"
