from netaddr import EUI


# class to check if the mac address is valid and store it
class MacAddress:
    """Class to check if the mac address is valid and store it"""

    mac: str = None

    def __init__(self, mac: str):
        try:
            self.___mac = str(EUI(mac)).replace("-", ":")
        except Exception as e:
            print(e)
            self.___mac = None

    def getMac(self):
        """
        Return the mac address
        """
        return self.___mac
