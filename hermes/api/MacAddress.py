from netaddr import EUI


class MacAddress:
    """
    Class to check if the mac address is valid and store it
    """

    mac: str = None

    def __init__(self, mac: str):
        try:
            self.___mac = str(EUI(mac)).replace(
                "-", ":"
            )  # Convert the mac address to the correct format
        except Exception as e:
            print(e)
            self.___mac = None

    def getMac(self):
        """
        Return the mac address
        """
        return self.___mac
