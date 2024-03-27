from netaddr import IPAddress, IPNetwork


class UNetId:
    """Object used to store the name of a user network id"""

    def __init__(self, unetid: str):
        self.name = unetid


class UCIConfig:
    """Mother class implementing the UCIConfig interface"""

    def __init__(self):
        pass

    def uci_build_string(self) -> str:
        """Used to create the set of uci command to use in the system

        Returns:
            str: Uci commands to execute
        """


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


# ---------------------------------------------------------------------------- #
#                                    Network                                   #
# ---------------------------------------------------------------------------- #


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

    def __init__(self, unetid: UNetId, name_prefix: str, ports: str = None):
        self.name = name_prefix + unetid.name
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

    def __init__(
        self,
        unetid: UNetId,
        name_prefix: str,
        ip: IPAddress,
        mask: IPAddress,
        bridge: Bridge = None,
    ):
        self.name = name_prefix + unetid.name
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


class Route(UCIConfig):
    """Used to create a network route

    Args:
        UCIConfig (UCIConfig): MotherClass
    """

    def __init__(
        self,
        unetid: UNetId,
        name_prefix: str,
        target: IPNetwork,
        gateway: IPAddress,
        interface: Interface,
    ):
        self.name = name_prefix + unetid.name
        self.target = target
        self.gateway = gateway
        self.interface = interface

    def uci_build_string(self):
        string = f"""uci set network.{self.name}=route
        uci set network.{self.name}.target='{self.target}'
        uci set network.{self.name}.gateway='{self.gateway}'
        uci set network.{self.name}.interface='{self.interface.name}'"""
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


# ---------------------------------------------------------------------------- #
#                                   Wireless                                   #
# ---------------------------------------------------------------------------- #


class WifiDevice(UCIConfig):
    """Used to create a wireless interface

    Args:
        UCIConfig (UCIConfig): MotherClass
    """

    def __init__(
        self,
        name: str,
        path: str,
        device_type: str,
        channel: int,
        htmode: str,
        country: str,
        band: str,
        disabled: str = "0",
    ):
        """Create a wifi device

        Args:
            name (str): radio0 or radio1 (for 2.4 and 5GHz)
            path (str): Path to the physical wifi device
            device_type (str): _description_
            channel (int): Wifi Channel number (Maybe be dynamic in the future)
            htmode (str): htmode see documentation
            country (str): FR, US, ...
            band (str): 5 or 2.4
            disabled (str, optional): Defaults to "0".
        """
        self.name = name
        self.path = path
        self.type = device_type
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

    def __init__(
        self,
        unetid: UNetId,
        device: WifiDevice,
        network: Interface,
        mode: str,
        ssid_prefix: str,
        encryption: str,
        key: str,
        disabled: str = "0",
    ):
        self.name = f"wifi_{unetid.name}_{device.name}"
        self.device = device
        self.network = network
        self.mode = mode
        self.ssid = ssid_prefix + unetid.name
        self.encryption = encryption
        self.key = key
        self.disabled = disabled

    def uci_build_string(self):
        string = f"""uci set wireless.{self.name}=wifi-iface
        uci set wireless.{self.name}.device='{self.device.name}'
        uci set wireless.{self.name}.network='{self.network.name}'
        uci set wireless.{self.name}.mode='{self.mode}'
        uci set wireless.{self.name}.ssid='{self.ssid}'
        uci set wireless.{self.name}.encryption='{self.encryption}'
        uci set wireless.{self.name}.key='{self.key}'
        uci set wireless.{self.name}.disabled='{self.disabled}'"""
        return string


# ---------------------------------------------------------------------------- #
#                                   Firewall                                   #
# ---------------------------------------------------------------------------- #


class Redirect4(UCIConfig):
    """Used to create a port redirection

    Args:
        UCIConfig (UCIConfig): MotherClass
    """

    def __init__(
        self,
        unetid: UNetId,
        desc: str,
        src: Interface,
        src_ip: IPAddress,
        src_dport: int,
        dest: Interface,
        dest_ip: IPAddress,
        dest_port: int,
        proto: str = "tcp",
    ):
        """
        Initialize a ClassConfig object.
        See: https://openwrt.org/docs/guide-user/firewall/firewall_configuration#redirects
        Args:
            unetid (UNetId): The UNetId object.
            desc (str): The description of the ClassConfig.
            src (Interface): The source interface.
            src_ip (IPAddress): The source IP
            src_dport (int): The source destination port.
            dest (Interface): The destination interface.
            dest_ip (IPAddress): The destination IP address.
            dest_port (int): The destination port.
            proto (str, optional): The protocol. Defaults to "tcp".
        """
        self.name = unetid.name + desc
        self.src = src
        self.src_ip = src_ip
        self.src_dport = src_dport
        self.dest = dest
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.proto = proto

    def uci_build_string(self):
        string = f"""uci set firewall.{self.name}=redirect
        uci set firewall.{self.name}.name='{self.name}'
        uci set firewall.{self.name}.target='DNAT'
        uci set firewall.{self.name}.src='{self.src.name}'
        uci set firewall.{self.name}.src_ip='{self.src_ip}'
        uci set firewall.{self.name}.src_dport='{self.src_dport}'
        uci set firewall.{self.name}.dest='{self.dest.name}'
        uci set firewall.{self.name}.dest_ip='{self.dest_ip}'
        uci set firewall.{self.name}.dest_port='{self.dest_port}'"""
        return string


class Forwarding(UCIConfig):
    """Used to create a port forwarding"""

    def __init__(self, src: Interface, dest: Interface):
        """
        Initialize a UCIConfig object.
        See: https://openwrt.org/docs/guide-user/firewall/firewall_configuration#forwardings
        Args:
            unetid (UNetId): The UNetId object.
            desc (str): The description of the ClassConfig.
            src (Interface): The source interface.
            dest (Interface): The destination interface.
        """
        self.name = "forwarding_" + src.name + "_" + dest.name
        self.src = src
        self.dest = dest

    def uci_build_string(self):
        string = f"""uci set firewall.{self.name}=forwarding
        uci set firewall.{self.name}.src='{self.src.name}'
        uci set firewall.{self.name}.dest='{self.dest.name}'"""
        return string


class Zone(UCIConfig):
    """Used to create a firewall zone"""

    def __init__(
        self,
        network: Interface,
        forwardings: list,
        input: str = "ACCEPT",
        output: str = "ACCEPT",
        forward: str = "ACCEPT",
    ):
        """
        Initialize a UCIConfig object.
        See: https://openwrt.org/docs/guide-user/firewall/firewall_configuration#zones
        Args:
            unetid (UNetId): The UNetId object.
            name (str): The name of the zone.
            network (Interface): The network interface.
            forwardings (list): The list of forwardings.
            redirects (list): The list of redirects.
        """
        self.name = "zone_" + network.name
        self.network = network
        self.forwardings = forwardings
        self.input = input
        self.output = output
        self.forward = forward

    def uci_build_string(self):
        string = f"""uci set firewall.{self.name}=zone
        uci set firewall.{self.name}.name='{self.name}'
        uci set firewall.{self.name}.network='{self.network.name}'
        uci set firewall.{self.name}.input='{self.input}'
        uci set firewall.{self.name}.output='{self.output}'
        uci set firewall.{self.name}.forward='{self.forward}'"""
        return string


class Rule(UCIConfig):
    """Used to create a firewall rule"""

    def __init__(
        self,
        unetid: UNetId,
        desc: str,
        dest_ip: IPAddress,
        dest: Interface,
        proto: str,
        target: str,
        src: Interface = None,
        src_ip: IPAddress = None,
        dest_port: int = None,
        family: str = "ipv4",
    ):
        """
        Initialize a UCIConfig object.
        See: https://openwrt.org/docs/guide-user/firewall/firewall_configuration#rules
        Args:
            unetid (UNetId): The UNetId object.
            name (str): The name of the rule.
            src (Interface): The source interface.
            dest (Interface): The destination interface.
            proto (str): The protocol.
            target (str): The target.
            dest_port (int, optional): The destination port. Defaults to None.
        """
        self.name = unetid.name + "_" + desc
        self.proto = proto
        self.src = src
        self.src_ip = src_ip
        self.dest = dest
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.target = target
        self.family = family

    def uci_build_string(self):
        string = f"""uci set firewall.{self.name}=rule
        uci set firewall.{self.name}.name='{self.name}'
        uci set firewall.{self.name}.dest='{self.dest.name}'
        uci set firewall.{self.name}.dest_ip='{self.dest_ip}'
        uci set firewall.{self.name}.proto='{self.proto}'
        uci set firewall.{self.name}.target='{self.target}'
        uci set firewall.{self.name}.family='{self.family}'"""
        if self.src is not None:
            string += f"""uci set firewall.{self.name}.src='{self.src.name}'"""
        if self.src_ip is not None:
            string += f"""uci set firewall.{self.name}.src_ip='{self.src_ip}'"""
        if self.dest_port is not None:
            string += f"""uci set firewall.{self.name}.dest_port='{self.dest_port}'"""
        return string


class Nat(UCIConfig):
    """Used to create a NAT rule"""

    def __init__(
        self,
        wan_interface: Interface,
        lan_interface: Interface,
    ):
        """
        Initialize a UCIConfig object.
        See: https://openwrt.org/docs/guide-user/firewall/firewall_configuration#source_nat
        Args:
            wan_interface (Interface): The WAN interface.
            lan_interface (Interface): The LAN interface.
        """
        self.name = "nat_" + lan_interface.name + "_to_" + wan_interface.name
        self.wan_interface = wan_interface
        self.lan_interface = lan_interface
        self.lan_network = IPNetwork(f"{lan_interface.ip}/{lan_interface.mask}").network

    def uci_build_string(self):  # TODO: Check SRC Interface
        string = f"""uci set firewall.{self.name}=nat
        uci set firewall.{self.name}.name='{self.name}'
        uci set firewall.{self.name}.target='SNAT'
        uci set firewall.{self.name}.snat_ip='{self.wan_interface.ip}'
        uci set firewall.{self.name}.src='{self.lan_interface.name}'
        uci set firewall.{self.name}.src_ip='{self.lan_network}'
        uci set firewall.{self.name}.proto='all'"""

        return string


# ---------------------------------------------------------------------------- #
#                                     DHCP                                     #
# ---------------------------------------------------------------------------- #


class DHCP(UCIConfig):
    """Used to create a DHCP server

    Args:
        UCIConfig (UCIConfig): MotherClass
    """

    def __init__(self, interface: Interface, start: int, limit: int, leasetime: int):
        self.name = interface.name
        self.interface = interface
        self.start = start
        self.limit = limit
        self.leasetime = leasetime

    def uci_build_string(self):
        string = f"""uci set dhcp.{self.name}=dhcp
        uci set dhcp.{self.name}.interface='{self.interface.name}'
        uci set dhcp.{self.name}.start='{self.start}'
        uci set dhcp.{self.name}.limit='{self.limit}'
        uci set dhcp.{self.name}.leasetime='{self.leasetime}'"""
        return string
