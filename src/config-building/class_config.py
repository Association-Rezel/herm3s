import re
from netaddr import IPAddress, IPNetwork
#TODO: Default conf

class Attribute:
    """Object used to store the name of an attribute
    """
    value: str

    def __init__(self):
        pass
    def __str__(self) -> str:
        return self.value

class UNetId:
    """Object used to store the name of a user network id"""
    value: str

    def __init__(self, unetid: str):
        if re.match(r"^[A-z0-9_\-]+$", unetid) is None:
            raise ValueError("Invalid UNetId")
        self.value = unetid
    def __str__(self) -> str:
        return self.value

class UCISectionName:
    """Object used to store the name of a network object"""
    value: str

    def __init__(self, value: str):
        if re.match(r"^[A-z0-9_\-]+$", value) is None:
            raise ValueError("Invalid Name")
        self.value = value
    def __str__(self) -> str:
        return self.value

class UCINetworkPorts:
    """Object used to store the ports of a network object"""
    ports: str

    def __init__(self, ports: str):
        if re.match(r"^[A-z0-9\-_\.]+(?:\s+[A-z0-9\-_\.]+)*$", ports) is None:
            raise ValueError("Invalid Ports")
        self.ports = ports
    def __str__(self) -> str:
        return self.ports

class UCISectionNamePrefix:
    """Object used to store the name prefix of a network object"""
    value: str
    def __init__(self, value: str):
        if re.match(r"^[A-z0-9_\-]+$", value) is None:
            raise ValueError("Invalid Name")
        self.value = value
    def __str__(self) -> str:
        return self.value

class UCIConfig:
    """Mother class implementing the UCIConfig interface"""
    name : UCISectionName
    optional_uci_commands: str

    def __init__(self, name: UCISectionName, optional_uci_commands: str = ""):
        self.name = name
        self.optional_uci_commands = optional_uci_commands

    def uci_build_string(self) -> str:
        """Used to create the set of uci command to use in the system

        Returns:
            str: Uci commands to execute
        """
        return self.optional_uci_commands

    def __str__(self) -> str:
        return self.name.value


class UCIApply(UCIConfig):
    """Used to apply the UCI configuration to the system
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
class InterfaceProto(Attribute):
    """Object used to store the protocol of a network interface
    """

    def __init__(self, value: str = "static"):
        if value not in ["static", "dhcp", "pppoe", "dhcpv6", "none"]:
            raise ValueError("Invalid Protocol")
        self.value = value

class Device:
    name: str

    """Class for devices-like objects"""
    def __init__(self):
        pass
    def __str__(self) -> str:
        return self.name

class UCINetGlobals(UCIConfig):
    """Used to create a global network configuration
    """
    ula_prefix: IPNetwork

    def __init__(self, ula_prefix: IPNetwork):
        super().__init__("globals")
        self.ula_prefix = ula_prefix

    def uci_build_string(self):
        string = f"""uci set network.{self}=globals
        uci set network.{self}.ula_prefix='{self.ula_prefix}'"""
        return string

class UCISwitch(UCIConfig):
    """Used to create a network switch
    """
    name: UCISectionName
    ports: UCINetworkPorts

    def __init__(self, name: UCISectionName, ports: UCINetworkPorts = None):
        super().__init__(name)
        self.ports = ports

    def uci_build_string(self):
        string = f"""uci set network.{self}=switch
        uci set network.{self}.name='{self}'
        uci set network.{self}.reset='1'
        uci set network.{self}.enable_vlan='1'"""
        if self.ports is not None:
            string += f"""uci set network.{self}.ports='{self.ports}'"""
        return string

class UCISimpleDevice(Device):
    """Object used to store the name of a device
    """

    def __init__(self, name: str):
        if re.match(r"^[A-z0-9\.]+$", name) is None:
            raise ValueError("Invalid Device")
        self.name = name

class UCIBridge(UCIConfig, Device):
    """Used to create a network bridge
    """
    ports: UCINetworkPorts

    def __init__(self, unetid: UNetId, name_prefix: UCISectionNamePrefix, ports: UCINetworkPorts = None):
        super().__init__(name_prefix.__str__() + unetid.__str__())
        self.ports = ports

    def uci_build_string(self):
        string = f"""uci set network.{self}=device
        uci set network.{self}.proto='bridge'
        uci set network.{self}.name='{self}'"""
        if self.ports is not None:
            string += f"""uci set network.{self}.ports='{self.ports}'"""
        return string

class UCIInterface(UCIConfig):
    """Used to create a network interface
    """
    ip: IPAddress
    mask: IPAddress
    device: Device

    def __init__(
        self,
        unetid: UNetId,
        name_prefix: UCISectionNamePrefix,
        ip: IPAddress,
        mask: IPAddress,
        proto: InterfaceProto,
        device: Device = None,
    ):
        super().__init__(name_prefix.__str__() + unetid.__str__())
        self.ip = ip
        self.mask = mask
        self.proto = proto
        self.device = device


    def uci_build_string(self):
        string = f"""uci set network.{self}=interface
        uci set network.{self}.proto='{self.proto}'
        uci set network.{self}.ipaddr='{self.ip}'
        uci set network.{self}.netmask='{self.mask}'
        uci commit network"""
        if self.device is not None:
            string += f"""uci set network.{self}.device='{self.device}'"""
        return string

class UCIRoute(UCIConfig):
    """Used to create a network route
    """

    def __init__(
        self,
        unetid: UNetId,
        name_prefix: UCISectionNamePrefix,
        target: IPNetwork,
        gateway: IPAddress,
        interface: UCIInterface,
    ):
        super().__init__(name_prefix.__str__() + unetid.__str__())
        self.target = target
        self.gateway = gateway
        self.interface = interface

    def uci_build_string(self):
        string = f"""uci set network.{self}=route
        uci set network.{self}.target='{self.target}'
        uci set network.{self}.gateway='{self.gateway}'
        uci set network.{self}.interface='{self.interface}'"""
        return string


class UCINoIPInterface(UCIConfig):
    """Used to create a network interface without an IP
    """

    def __init__(self, name: UCISectionName, device: Device):
        super().__init__(name)
        self.device = device

    def uci_build_string(self):
        string = f"""uci set network.{self}=interface
        uci set network.{self}.device={self.device}"""
        return string


class UCISwitchVlan(UCIConfig):
    """Used to create a VLAN on a switch
    """
    name: UCISectionName
    device: UCISwitch
    vlan: int
    vid: int
    ports: UCINetworkPorts

    def __init__(self, name: UCISectionName, device: UCISwitch, vid: int, ports: UCINetworkPorts):
        super().__init__(name)
        self.device = device
        self.vlan = vid
        self.vid = vid
        self.ports = ports

    def uci_build_string(self):
        string = f"""uci set network.{self}=switch_vlan
        uci set network.{self}.device='{self.device}'
        uci set network.{self}.vlan='{self.vid}'
        uci set network.{self}.ports='{self.ports}'"""
        return string


# ---------------------------------------------------------------------------- #
#                                   Wireless                                   #
# ---------------------------------------------------------------------------- #

class Path(Attribute):
    """Object used to store the path of a device
    """

    def __init__(self, value: str):
        if re.match(r"^[A-z0-9_\-:\.]+$", value) is None:
            raise ValueError("Invalid Path")
        self.value = value
    
class DeviceType(Attribute):
    """Object used to store the type of a device
    """

    def __init__(self, value: str):
        if re.match(r"^[A-z0-9]+$", value) is None:
            raise ValueError("Invalid Device Type")
        self.value = value

class Htmode(Attribute):
    """Object used to store the htmode of a device
    """

    def __init__(self, value: str):
        if re.match(r"^[A-z0-9]+$", value) is None:
            raise ValueError("Invalid htmode")
        self.value = value

class Country(Attribute):
    """Object used to store the country of a device
    """

    def __init__(self, value: str):
        if re.match(r"^[A-Z]+$", value) is None:
            raise ValueError("Invalid Country")
        self.value = value

class Band(Attribute):
    """Object used to store the band of a device
    """

    def __init__(self, value: str):
        if re.match(r"^[a-z0-9]+$", value) is None:
            raise ValueError("Invalid Band")
        self.value = value


class Mode(Attribute):
    """Object used to store the mode of a wifi interface
    """

    def __init__(self, value: str):
        if value not in ["sta", "ap", "adhoc", "monitor", "mesh"]:
            raise ValueError("Invalid Mode")
        self.value = value

class SSID(Attribute):
    """Object used to store the ssid of a wifi interface
    """

    def __init__(self, ssid_prefix: str, ssid_suffix:str):
        value = ssid_prefix + ssid_suffix
        if re.match(r"^[A-z0-9_]{1,32}$", value) is None:
            raise ValueError("Invalid SSID")
        self.value = value

class Encryption(Attribute):
    """Object used to store the encryption of a wifi interface
    """

    def __init__(self, value: str):
        if re.match(r"^[a-z0-9\+\-]{8,63}$", value) is None:
            raise ValueError("Invalid Encryption")
        self.value = value

class Key(Attribute):
    """Object used to store the key of a wifi interface
    """

    def __init__(self, value: str):
        if re.match(r"^[\x21-\x7E]{8,63}$", value) is None:
            raise ValueError("Invalid Key")
        self.value = value

class UCIWifiDevice(UCIConfig):
    """Used to create a wireless interface
    """
    path: Path
    type: DeviceType
    channel: int
    htmode: Htmode
    country: Country
    band: Band
    disabled: int

    def __init__(
        self,
        name: UCISectionName,
        path: Path,
        device_type: DeviceType,
        channel: int,
        htmode: Htmode,
        country: Country,
        band: Band,
        disabled: int = 0,
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
        super().__init__(name)
        self.path = path
        self.type = device_type
        self.channel = channel
        self.htmode = htmode
        self.country = country
        self.band = band
        self.disabled = disabled

    def uci_build_string(self):
        string = f"""uci set wireless.{self}=wifi-device
        uci set wireless.{self}.type='{self.type}'
        uci set wireless.{self}.path='{self.path}'
        uci set wireless.{self}.channel='{self.channel}'
        uci set wireless.{self}.htmode='{self.htmode}'
        uci set wireless.{self}.country='{self.country}'
        uci set wireless.{self}.band='{self.band}'
        uci set wireless.{self}.disabled='{self.disabled}'"""
        return string

class WifiIface(UCIConfig):

    def __init__(
        self,
        unetid: UNetId,
        device: UCIWifiDevice,
        network: UCIInterface,
        mode: Mode,
        ssid: SSID,
        encryption: Encryption,
        key: Key,
        disabled: int = 0,
    ):
        super().__init__(f"wifi_{unetid}_{device}")
        self.device = device
        self.network = network
        self.mode = mode
        self.ssid = ssid
        self.encryption = encryption
        self.key = key
        self.disabled = disabled

    def uci_build_string(self):
        string = f"""uci set wireless.{self}=wifi-iface
        uci set wireless.{self}.device='{self.device}'
        uci set wireless.{self}.network='{self.network}'
        uci set wireless.{self}.mode='{self.mode}'
        uci set wireless.{self}.ssid='{self.ssid}'
        uci set wireless.{self}.encryption='{self.encryption}'
        uci set wireless.{self}.key='{self.key}'
        uci set wireless.{self}.disabled='{self.disabled}'"""
        return string


# ---------------------------------------------------------------------------- #
#                                   Firewall                                   #
# ---------------------------------------------------------------------------- #
class Description(Attribute):
    """Object used to store the description of a firewall rule
    """

    def __init__(self, value: str):
        if re.match(r"^[A-z0-9_\- ]+$", value) is None:
            raise ValueError("Invalid Description")
        self.value = value

class TCPUDPPort(Attribute):
    """Object used to store the port of a firewall rule
    """

    def __init__(self, value: int):
        if value < 0 or value > 65535:
            raise ValueError("Invalid Port")
        self.value = str(value)

class Protocol(Attribute):
    """Object used to store the protocol of a firewall rule
    """

    def __init__(self, value: str = "tcp"):
        if value not in ["tcp", "udp", "udplite", "icmp", "ah", "esp", "sctp" "all"]:
            raise ValueError("Invalid Protocol")
        self.value = value

class InOutForw(Attribute):
    """Object used to store the in/out/forward of a firewall zone
    """

    def __init__(self, value: str = "ACCEPT"):
        if value not in ["ACCEPT", "REJECT", "DROP"]:
            raise ValueError("Invalid In/Out/Forward")
        self.value = value

class Target(Attribute):
    """Object used to store the target of a firewall rule
    """

    def __init__(self, value: str = "ACCEPT"):
        if value not in ["ACCEPT", "REJECT", "DROP", "MARK", "NOTRACK"]:
            raise ValueError("Invalid Target")
        self.value = value

class Family(Attribute):
    """Object used to store the family of a firewall rule
    """

    def __init__(self, value: str = "ipv4"):
        if value not in ["ipv4", "ipv6", "any"]:
            raise ValueError("Invalid Family")
        self.value = value

class UCIFirewallDefaults(UCIConfig):
    """Used to create a default firewall configuration
    """

    def __init__(self):
        super().__init__("defaults")

    def uci_build_string(self):
        string = f"""uci set firewall.{self}=defaults
        uci set firewall.{self}.syn_flood='1'
        uci set firewall.{self}.flow_offloading='1'
        uci set firewall.{self}.flow_offloading_hw='1'
        uci set firewall.{self}.input='ACCEPT'
        uci set firewall.{self}.output='ACCEPT'
        uci set firewall.{self}.forward='REJECT'"""
        return string

class UCIRedirect4(UCIConfig):
    """Used to create a port redirection
    """
    desc: Description
    src: UCIInterface
    src_ip: IPAddress
    src_dport: TCPUDPPort
    dest: UCIInterface
    dest_ip: IPAddress
    dest_port: TCPUDPPort
    proto: Protocol


    def __init__(
        self,
        unetid: UNetId,
        name: UCISectionName,
        desc: Description,
        src: UCIInterface,
        src_ip: IPAddress,
        src_dport: TCPUDPPort,
        dest: UCIInterface,
        dest_ip: IPAddress,
        dest_port: TCPUDPPort,
        proto: Protocol,
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
        super().__init__(f"{unetid}_{name}")
        self.desc = desc
        self.src = src
        self.src_ip = src_ip
        self.src_dport = src_dport
        self.dest = dest
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.proto = proto

    def uci_build_string(self):
        string = f"""uci set firewall.{self}=redirect
        uci set firewall.{self}.name='{self.desc}'
        uci set firewall.{self}.target='DNAT'
        uci set firewall.{self}.src='{self.src}'
        uci set firewall.{self}.src_ip='{self.src_ip}'
        uci set firewall.{self}.src_dport='{self.src_dport}'
        uci set firewall.{self}.dest='{self.dest}'
        uci set firewall.{self}.dest_ip='{self.dest_ip}'
        uci set firewall.{self}.dest_port='{self.dest_port}'"""
        return string


class UCIForwarding(UCIConfig):
    """Used to create a port forwarding"""

    def __init__(self, src: UCIInterface, dest: UCIInterface):
        """
        Initialize a UCIConfig object.
        See: https://openwrt.org/docs/guide-user/firewall/firewall_configuration#forwardings
        Args:
            unetid (UNetId): The UNetId object.
            desc (str): The description of the ClassConfig.
            src (Interface): The source interface.
            dest (Interface): The destination interface.
        """
        super().__init__(f"forwarding_{src}_{dest}")
        self.src = src
        self.dest = dest

    def uci_build_string(self):
        string = f"""uci set firewall.{self}=forwarding
        uci set firewall.{self}.src='{self.src}'
        uci set firewall.{self}.dest='{self.dest}'"""
        return string

class UCIZone(UCIConfig):
    """Used to create a firewall zone"""

    network: UCIInterface
    input: InOutForw
    output: InOutForw
    forward: InOutForw

    def __init__(
        self,
        network: UCIInterface,
        _input: InOutForw,
        output: InOutForw,
        forward: InOutForw,
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
        super().__init__(f"zone_{network}")
        self.network = network
        self.input = _input
        self.output = output
        self.forward = forward

    def uci_build_string(self):
        string = f"""uci set firewall.{self}=zone
        uci set firewall.{self}.name='{self}'
        uci set firewall.{self}.network='{self.network}'
        uci set firewall.{self}.input='{self.input}'
        uci set firewall.{self}.output='{self.output}'
        uci set firewall.{self}.forward='{self.forward}'"""
        return string

class UCIRule(UCIConfig):
    """Used to create a firewall rule"""

    desc: Description
    proto: Protocol
    src: UCIInterface
    src_ip: IPAddress
    src_port: TCPUDPPort
    dest: UCIInterface
    dest_ip: IPAddress
    dest_port: TCPUDPPort
    target: Target
    family: Family

    def __init__(
        self,
        unetid: UNetId,
        name: UCISectionName,
        desc: Description,
        dest_ip: IPAddress,
        dest: UCIInterface,
        proto: Protocol,
        target: Target,
        src: UCIInterface = None,
        src_ip: IPAddress = None,
        src_port: TCPUDPPort = None,
        dest_port: TCPUDPPort = None,
        family: Family = "ipv4",
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
        super().__init__(f"{unetid}_{name}")
        self.desc = desc
        self.proto = proto
        self.src = src
        self.src_ip = src_ip
        self.src_port = src_port
        self.dest = dest
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.target = target
        self.family = family

    def uci_build_string(self):
        string = f"""uci set firewall.{self}=rule
        uci set firewall.{self}.name='{self.desc}'
        uci set firewall.{self}.dest='{self.dest}'
        uci set firewall.{self}.dest_ip='{self.dest_ip}'
        uci set firewall.{self}.proto='{self.proto}'
        uci set firewall.{self}.target='{self.target}'
        uci set firewall.{self}.family='{self.family}'"""
        if self.src is not None:
            string += f"""uci set firewall.{self}.src='{self.src}'"""
        if self.src_ip is not None:
            string += f"""uci set firewall.{self}.src_ip='{self.src_ip}'"""
        if self.src_port is not None:
            string += f"""uci set firewall.{self}.src_port='{self.src_port}'"""
        if self.dest_port is not None:
            string += f"""uci set firewall.{self}.dest_port='{self.dest_port}'"""
        return string


class UCISNat(UCIConfig):
    """Used to create a NAT rule"""
    wan_interface: UCIInterface
    lan_interface: UCIInterface
    lan_network: IPNetwork

    def __init__(
        self,
        wan_interface: UCIInterface,
        lan_interface: UCIInterface,
    ):
        """
        Initialize a UCIConfig object.
        See: https://openwrt.org/docs/guide-user/firewall/firewall_configuration#source_nat
        Args:
            wan_interface (UCIInterface): The WAN interface.
            lan_interface (UCIInterface): The LAN interface.
        """
        super().__init__(f"nat_{lan_interface}_to_{wan_interface}")
        self.wan_interface = wan_interface
        self.lan_interface = lan_interface
        self.lan_network = IPNetwork(f"{lan_interface.ip}/{lan_interface.mask}").network

    def uci_build_string(self):  # TODO: Check SRC Interface
        string = f"""uci set firewall.{self}=nat
        uci set firewall.{self}.name='{self}'
        uci set firewall.{self}.target='SNAT'
        uci set firewall.{self}.snat_ip='{self.wan_interface.ip}'
        uci set firewall.{self}.src='{self.lan_interface}'
        uci set firewall.{self}.src_ip='{self.lan_network}'
        uci set firewall.{self}.proto='all'"""

        return string


# ---------------------------------------------------------------------------- #
#                                     DHCP                                     #
# ---------------------------------------------------------------------------- #
class DnsServers(Attribute):
    """Object used to store the DNS servers of a DHCP server
    """

    def __init__(self, value: list[IPAddress]):
        for ip in value:
            if not isinstance(ip, IPAddress):
                raise ValueError("Invalid DNS Servers")
        self.value = value

class UCIdnsmasq(UCIConfig):
    """Used to create a DNS server
    """
    dns_servers: DnsServers

    def __init__(self, dns_servers: DnsServers):
        super().__init__(f"dnsmasq")
        self.dns_servers = dns_servers
    def uci_build_string(self):
        string = f"""uci set dhcp.{self}=dnsmasq
        uci set dhcp.{self}.domainneeded='1'
        uci set dhcp.{self}.authoritative='1'
        uci set dhcp.{self}.rebind_protection='1'
        uci set dhcp.{self}.rebind_localhost='1'
        uci set dhcp.{self}.localise_queries='1'
        uci set dhcp.{self}.filterwin2k='0'
        uci set dhcp.{self}.local='/lan/'
        uci set dhcp.{self}.domain='lan'
        uci set dhcp.{self}.expandhosts='1'
        uci set dhcp.{self}.nonegcache='0'
        uci set dhcp.{self}.readethers='1'
        uci set dhcp.{self}.leasefile='/tmp/dhcp.leases'
        uci set dhcp.{self}.resolvfile='/tmp/resolv.conf.auto'
        uci set dhcp.{self}.nonwildcard='1'
        uci set dhcp.{self}.localservice='1'
        uci set dhcp.{self}.ednspacket_max='1232'"""
        for dns in self.dns_servers:
            string += f"""uci add_list dhcp.{self}.server='{dns}'"""
        return string

class UCIodchp(UCIConfig):
    """Used to create a DHCP server
    """

    def __init__(self,loglevel: int = 4):
        super().__init__("odhcpd")
        self.loglevel = loglevel

    def uci_build_string(self):
        string = f"""uci set dhcp.{self}=odhcpd
        uci set dhcp.{self}.maindhcp='0'
        uci set dhcp.{self}.leasefile='/tmp/hosts/odhcpd'
        uci set dhcp.{self}.leasetrigger='/usr/sbin/odhcpd-update'
        uci set dhcp.{self}.loglevel='{self.loglevel}'"""
        return string

class UCIDHCP(UCIConfig):
    """Used to create a DHCP server
    """

    def __init__(
            self,
            interface: UCIInterface,
            start: int,
            limit: int,
            leasetime: int
            ):
        super().__init__(f"dhcp_{interface}")
        self.interface = interface
        self.start = start
        self.limit = limit
        self.leasetime = leasetime

    def uci_build_string(self):
        string = f"""uci set dhcp.{self}=dhcp
        uci set dhcp.{self}.interface='{self.interface}'
        uci set dhcp.{self}.start='{self.start}'
        uci set dhcp.{self}.limit='{self.limit}'
        uci set dhcp.{self}.leasetime='{self.leasetime}'"""
        return string

# ---------------------------------------------------------------------------- #
#                                   Dropbear                                   #
# ---------------------------------------------------------------------------- #
class UCIDropbear(UCIConfig):
    """Used to create a Dropbear configuration
    """

    def __init__(self):
        super().__init__("dropbear")

    def uci_build_string(self):
        string = f"""uci set dropbear.{self}=dropbear
        uci set dropbear.{self}.PasswordAuth='off'
        uci set dropbear.{self}.RootPasswordAuth='off'
        uci set dropbear.{self}.Port='22'"""
        return string