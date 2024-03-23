from netaddr import IPAddress

class UCIConfig:
    def __init__(self):
        pass
    def uci_build_string(self) -> str:
        pass

class UCIApply(UCIConfig):
    """Used to apply the UCI configuration to the system

    Args:
        UCIConfig (UCIConfig): MotherClass
    """
    def __init__(self):
        pass
    def uci_build_string(self):
        string = """uci commit
        service conf-init disable    
        service conf-sync enable
        service dropbear restart 
        service firewall restart
        service dnsmasq restart
        service odhcpd restart
        wifi reload
        service network restart"""
        return string
    
class Switch(UCIConfig):
    """Used to create a network switch

    Args:
        UCIConfig (UCIConfig): MotherClass
    """
    def __init__(self, name: str, ports: str = None):
        self.name = name
        self.ports = ports
    def uci_build_string(self):
        string = f"""uci set network.{self.name}=switch
        uci set network.{self.name}.name='{self.name}'
        uci set network.{self.name}.reset='1'
        uci set network.{self.name}.enable_vlan='1'"""
        return string
    
class Bridge(UCIConfig):
    """Used to create a network bridge

    Args:
        UCIConfig (UCIConfig): MotherClass
    """
    def __init__(self, name: str, ports: str = None):
        self.name = "br_lan_"+name
        self.ports = ports

    def uci_build_string(self):
        string = f"""uci set network.{self.name}=device
        uci set network.{self.name}.proto='bridge'
        uci set network.{self.name}.name='{self.name}'"""
        if self.ports is not None:
            string += f"""uci set network.{self.name}.ports='{self.ports}'"""
        return string

class Interface(UCIConfig):
    """Used to create a network interface

    Args:
        UCIConfig (UCIConfig): MotherClass
    """
    def __init__(self, name: str, name_prefix: str, ip: IPAddress, mask: IPAddress, bridge: Bridge = None):
        self.name = name_prefix + name
        self.ip = ip
        self.mask = mask
        self.bridge = bridge
    def uci_build_string(self): 
        string = f"""uci set network.{self.name}=interface
        uci set network.{self.name}.proto='static'
        uci set network.{self.name}.ipaddr='{self.ip}'
        uci set network.{self.name}.netmask='{self.mask}'
        uci commit network"""
        if self.bridge is not None:
            string += f"""uci set network.{self.name}.device='{self.bridge.name}'"""

        return string

class NoIPInterface(UCIConfig):
    """Used to create a network interface without an IP

    Args:
        UCIConfig (UCIConfig): MotherClass
    """
    def __init__(self, name: str, device: str):
        self.name = name
        self.device = device
    def uci_build_string(self): 
        string = f"""uci set network.{self.name}=interface
        uci set network.{self.name}.device={self.device}"""
        return string

class WifiDevice(UCIConfig):
    """Used to create a wireless interface

    Args:
        UCIConfig (UCIConfig): MotherClass
    """
    def __init__(self, name: str,
                 path: str,
                 type: str,
                 channel: int,
                 htmode: str,
                 country: str,
                 band: str,
                 disabled: str = '0'):
        self.name = name
        self.path = path
        self.type = type
        self.channel = channel
        self.htmode = htmode
        self.country = country
        self.band = band
        self.disabled = disabled
    def uci_build_string(self):
        string = f"""uci set wireless.{self.name}=wifi-device
        uci set wireless.{self.name}.type='{self.type}'
        uci set wireless.{self.name}.path='{self.path}'
        uci set wireless.{self.name}.channel='{self.channel}'
        uci set wireless.{self.name}.htmode='{self.htmode}'
        uci set wireless.{self.name}.country='{self.country}'
        uci set wireless.{self.name}.band='{self.band}'
        uci set wireless.{self.name}.disabled='{self.disabled}'"""
        return string

class WifiIface(UCIConfig):
    """Used to create a wireless interface

    Args:
        UCIConfig (UCIConfig): MotherClass
    """
    def __init__(self, name: str,
                 device: WifiDevice,
                 network: Interface,
                 mode: str,
                 ssid_prefix: str,
                 encryption: str,
                 key: str,
                 disabled: str = '0'):
        self.name = f"wifi_{name}_{device.name}"
        self.device = device.name
        self.network = network.name
        self.mode = mode
        self.ssid = ssid_prefix + name
        self.encryption = encryption
        self.key = key
        self.disabled = disabled
    def uci_build_string(self):
        string = f"""uci set wireless.{self.name}=wifi-iface
        uci set wireless.{self.name}.device='{self.device.name}'
        uci set wireless.{self.name}.network='{self.network}'
        uci set wireless.{self.name}.mode='{self.mode}'
        uci set wireless.{self.name}.ssid='{self.ssid}'
        uci set wireless.{self.name}.encryption='{self.encryption}'
        uci set wireless.{self.name}.key='{self.key}'
        uci set wireless.{self.name}.disabled='{self.disabled}'"""
        return string

class SwitchVlan(UCIConfig):
    """Used to create a VLAN on a switch

    Args:
        UCIConfig (UCIConfig): MotherClass
    """
    def __init__(self, name: str, device: Switch, vid: int, ports: str):
        self.name = name
        self.device = device
        self.vlan = vid
        self.vid = vid
        self.ports = ports
    def uci_build_string(self):
        string = f"""uci set network.{self.name}=switch_vlan
        uci set network.{self.name}.device='{self.device.name}'
        uci set network.{self.name}.vlan='{self.vid}'
        uci set network.{self.name}.ports='{self.ports}'"""
        return string

