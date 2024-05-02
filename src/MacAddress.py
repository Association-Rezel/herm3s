from netaddr import EUI
#class to check if the mac address is valid and store it
class MacAddress:
    """Class to check if the mac address is valid and store it"""
    mac : str = None;
    def __init__(self, mac:str):
        try:
            self.mac = str(EUI(mac)).replace("-", ":")
        except Exception as e:
            None 
    def getMac(self):
        return self.mac