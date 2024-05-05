# change the default router ip address here
class Config:
    """
    Class to store global parameters
    """

    default_router_ip_address_vlan: dict = {101: "137.194.11.254", 102: "195.14.28.254"}
    default_path_files_saving: str = "/dev/shm/"
