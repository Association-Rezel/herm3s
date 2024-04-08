import re
from netaddr import IPAddress, IPNetwork

class Attribute:
    """Intrerface for attribute of UCIConfig objects"""

    value: str

    def __init__(self):
        """Initialize the Attribute object"""

    def __str__(self) -> str:
        """Return the string representation of the Attribute object"""
        return self.value


class UNetId(Attribute):
    """Object used to store the name of a user network id"""

    value: str

    def __init__(self, unetid: str):
        """Initialize the UNetId object

        Args:
            unetid (str): The name of the user network id
        """
        if re.match(r"^[A-z0-9_\-]+$", unetid) is None:
            raise ValueError("Invalid UNetId")
        self.value = unetid


class UCISectionName:
    """Object used to store the name of a UCIConfig section"""

    value: str

    def __init__(self, value: str):
        """Initialize the UCISectionName object

        Args:
            value (str): The name of the network object
        """
        if re.match(r"^[A-z0-9_\-]+$", value) is None:
            raise ValueError("Invalid Name")
        self.value = value

    def __str__(self) -> str:
        """Return the string representation of the UCISectionName object"""
        return self.value

class UCISectionNamePrefix:
    """Object used to store the prefi of a UCIConfig section
    e.g. Rezel_ or wifi_ """

    value: str

    def __init__(self, value: str):
        """Initialize the UCISectionNamePrefix object

        Args:
            value (str): The name prefix of the network object
        """
        if re.match(r"^[A-z0-9_\-]+$", value) is None:
            raise ValueError("Invalid Name")
        self.value = value

    def __str__(self) -> str:
        """Return the string representation of the UCISectionNamePrefix object"""
        return self.value


class UCINetworkPorts:
    """Object used to store the UCI Network ports
    e.g. 'eth0 eth1' or 'eth0.1 eth0.2' or '0t 1'
    """
    ports: str

    def __init__(self, ports: str):
        """Initialize the UCINetworkPorts object

        Args:
            ports (str): The ports of the network object
        """
        if re.match(r"^[A-z0-9\-_\.]+(?:\s+[A-z0-9\-_\.]+)*$", ports) is None:
            raise ValueError("Invalid Ports")
        self.ports = ports

    def __str__(self) -> str:
        """Return the string representation of the UCINetworkPorts object"""
        return self.ports


class UCIConfig:
    """Interface (almost) for UCI configuration objects
    """

    name: UCISectionName
    optional_uci_commands: str

    def __init__(self, name: UCISectionName, optional_uci_commands: str = ""):
        """Initialize the UCIConfig object

        Args:
            name (UCISectionName): The name of the network object
            optional_uci_commands (str, optional): Optional UCI commands. Defaults to "".
        """
        if isinstance(name, str):
            name = UCISectionName(name)
        self.name = name
        self.optional_uci_commands = optional_uci_commands

    def uci_build_string(self) -> str:
        """Used to create the set of uci command to use in the system

        Returns:
            str: Uci commands to execute
        """
        return self.optional_uci_commands

    def __str__(self) -> str:
        """Return the name of the network object"""
        return self.name.value

# ---------------------------------------------------------------------------- #
#                                    Network                                   #
# ---------------------------------------------------------------------------- #
class InterfaceProto(Attribute):
    """Object used to store the protocol of a network interface"""

    def __init__(self, value: str = "static"):
        """Initialize the InterfaceProto object

        Args:
            value (str, optional): The protocol value. Defaults to "static".

        Raises:
            ValueError: If the protocol value is invalid.
        """
        if value not in ["static", "dhcp", "pppoe", "dhcpv6", "none"]:
            raise ValueError("Invalid Protocol")
        self.value = value


class Device:
    """Class for devices-like objects"""

    name: str

    def __init__(self):
        """Initialize the Device object"""

    def __str__(self) -> str:
        """Return the string representation of the Device object

        Returns:
            str: The string representation of the Device object.
        """
        return self.name

class UCISimpleDevice(Device):
    """Object used to store the name of a device"""

    def __init__(self, name: str):
        """Initialize the UCISimpleDevice object

        Args:
            name (str): The name of the device.

        Raises:
            ValueError: If the device name is invalid.
        """
        if re.match(r"^[A-z0-9\.]+$", name) is None:
            raise ValueError("Invalid Device")
        self.name = name


class UCIBridge(UCIConfig, Device):
    """Represents a network bridge in uci
    See https://openwrt.org/docs/guide-user/network/network_configuration#section_device
    """

    ports: UCINetworkPorts

    def __init__(
        self,
        unetid: UNetId,
        name_prefix: UCISectionNamePrefix,
        ports: UCINetworkPorts = None,
    ):
        """Initialize the UCIBridge object

        Args:
            unetid (UNetId): The UNetId object.
            name_prefix (UCISectionNamePrefix): The UCISectionNamePrefix object.
            ports (UCINetworkPorts, optional): The ports of the bridge. Defaults to None.
        """
        super().__init__(name_prefix.__str__() + unetid.__str__())
        self.ports = ports

    def uci_build_string(self):
        """Build the UCI configuration string for UCIBridge

        Returns:
            str: The UCI configuration string.
        """
        string = f"""uci set network.{self}=device
uci set network.{self}.proto='bridge'
uci set network.{self}.name='{self}'
"""
        if self.ports is not None:
            string += f"""uci set network.{self}.ports='{self.ports}'
"""
        return string


class UCINetGlobals(UCIConfig):
    """Used to create a global network configuration
    See https://openwrt.org/docs/guide-user/network/network_configuration#section_globals 
    """

    ula_prefix: IPNetwork

    def __init__(self, ula_prefix: IPNetwork):
        """Initialize the UCINetGlobals object

        Args:
            ula_prefix (IPNetwork): The ULA prefix.
        """
        super().__init__("globals")
        self.ula_prefix = ula_prefix

    def uci_build_string(self):
        """Build the UCI configuration string for UCINetGlobals

        Returns:
            str: The UCI configuration string.
        """
        string = f"""uci set network.{self}=globals
uci set network.{self}.ula_prefix='{self.ula_prefix}'
"""
        return string


class UCISwitch(UCIConfig):
    """Used to create a network switch
    See https://openwrt.org/docs/guide-user/network/network_configuration#section_switch
    """

    name: UCISectionName
    ports: UCINetworkPorts

    def __init__(self, name: UCISectionName, ports: UCINetworkPorts = None):
        """Initialize the UCISwitch object

        Args:
            name (UCISectionName): The name of the switch.
            ports (UCINetworkPorts, optional): The ports of the switch. Defaults to None.
        """
        super().__init__(name)
        self.ports = ports

    def uci_build_string(self):
        """Build the UCI configuration string for UCISwitch

        Returns:
            str: The UCI configuration string.
        """
        string = f"""uci set network.{self}=switch
uci set network.{self}.name='{self}'
uci set network.{self}.reset='1'
uci set network.{self}.enable_vlan='1'
"""
        if self.ports is not None:
            string += f"""uci set network.{self}.ports='{self.ports}'
"""
        return string


class UCIInterface(UCIConfig):
    """Represents a network interface in uci
    See https://openwrt.org/docs/guide-user/network/network_configuration#section_interface
    """
    ip: IPAddress
    mask: IPAddress
    device: Device

    def __init__(
        self,
        name_prefix: UCISectionNamePrefix,
        ip: IPAddress,
        mask: IPAddress,
        proto: InterfaceProto,
        unetid: UNetId = None,
        device: Device = None,
    ):
        """Initialize the UCIInterface object

        Args:
            unetid (UNetId): The UNetId object.
            name_prefix (UCISectionNamePrefix): The UCISectionNamePrefix object.
            ip (IPAddress): The IP address e.g. 192.168.1.1.
            mask (IPAddress): The subnet mask e.g. 255.255.255.0.
            proto (InterfaceProto): The InterfaceProto object.
            device (Device, optional): The Device object. Defaults to None.
        """
        super().__init__(name_prefix.__str__() + unetid.__str__())
        self.ip = ip
        self.mask = mask
        self.proto = proto
        self.device = device

    def uci_build_string(self):
        """Build the UCI configuration string for UCIInterface

        Returns:
            str: The UCI configuration string.
        """
        string = f"""uci set network.{self}=interface
uci set network.{self}.proto='{self.proto}'
uci set network.{self}.ipaddr='{self.ip}'
uci set network.{self}.netmask='{self.mask}'
"""
        if self.device is not None:
            string += f"""uci set network.{self}.device='{self.device}'
"""
        return string


class UCIRoute(UCIConfig):
    """Used to create a network route
    See https://openwrt.org/docs/guide-user/network/routing/routes_configuration#static_routes
    """

    def __init__(
        self,
        unetid: UNetId,
        name_prefix: UCISectionNamePrefix,
        target: IPNetwork,
        gateway: IPAddress,
        interface: UCIInterface,
    ):
        """Initialize the UCIRoute object

        Args:
            unetid (UNetId): The UNetId object.
            name_prefix (UCISectionNamePrefix): The UCISectionNamePrefix object.
            target (IPNetwork): The target IP network.
            gateway (IPAddress): The gateway IP address.
            interface (UCIInterface): The UCIInterface object.
        """
        super().__init__(name_prefix.__str__() + unetid.__str__())
        self.target = target
        self.gateway = gateway
        self.interface = interface

    def uci_build_string(self):
        """Build the UCI configuration string for UCIRoute

        Returns:
            str: The UCI configuration string.
        """
        string = f"""uci set network.{self}=route
uci set network.{self}.target='{self.target}'
uci set network.{self}.gateway='{self.gateway}'
uci set network.{self}.interface='{self.interface}'
"""
        return string


class UCINoIPInterface(UCIConfig):
    """Used to create a network interface without an IP
    See https://openwrt.org/docs/guide-user/network/network_configuration#section_interface
    """

    def __init__(self, name: UCISectionName, device: Device):
        """Initialize the UCINoIPInterface object

        Args:
            name (UCISectionName): The name of the interface.
            device (Device): The Device object (SimpleDevice or Bridge).
        """
        super().__init__(name)
        self.device = device

    def uci_build_string(self):
        """Build the UCI configuration string for UCINoIPInterface

        Returns:
            str: The UCI configuration string.
        """
        string = f"""uci set network.{self}=interface
uci set network.{self}.device={self.device}
"""
        return string


class UCISwitchVlan(UCIConfig):
    """Used to create a VLAN on a switch
    See https://openwrt.org/docs/guide-user/network/network_configuration#section_switch_vlan
    """

    name: UCISectionName
    device: UCISwitch
    vlan: int
    vid: int
    ports: UCINetworkPorts

    def __init__(
        self, name: UCISectionName, device: UCISwitch, vid: int, ports: UCINetworkPorts
    ):
        """Initialize the UCISwitchVlan object

        Args:
            name (UCISectionName): The name of the VLAN.
            device (UCISwitch): The UCISwitch object.
            vid (int): The VLAN ID.
            ports (UCINetworkPorts): The ports of the VLAN.
        """
        super().__init__(name)
        self.device = device
        self.vlan = vid
        self.vid = vid
        self.ports = ports

    def uci_build_string(self):
        """Build the UCI configuration string for UCISwitchVlan

        Returns:
            str: The UCI configuration string.
        """
        string = f"""uci set network.{self}=switch_vlan
uci set network.{self}.device='{self.device}'
uci set network.{self}.vlan='{self.vid}'
uci set network.{self}.ports='{self.ports}'
"""
        return string


# ---------------------------------------------------------------------------- #
#                                   Wireless                                   #
# ---------------------------------------------------------------------------- #

class Path(Attribute):
    """Object used to store the path of a device"""

    def __init__(self, value: str):
        """
        Initialize a Path object.

        Args:
            value (str): The path of the device.

        Raises:
            ValueError: If the path is invalid.
        """
        if re.match(r"^[A-z0-9_\-:\.\/]+$", value) is None:
            raise ValueError("Invalid Path")
        self.value = value


class WifiDeviceType(Attribute):
    """Object used to store the type of a device"""

    def __init__(self, value: str):
        """
        Initialize a DeviceType object.

        Args:
            value (str): The type of the device.

        Raises:
            ValueError: If the device type is invalid.
        """
        if re.match(r"^[A-z0-9]+$", value) is None:
            raise ValueError("Invalid Device Type")
        self.value = value


class Htmode(Attribute):
    """Object used to store the htmode of a device"""

    def __init__(self, value: str):
        """
        Initialize a Htmode object.

        Args:
            value (str): The htmode of the device.

        Raises:
            ValueError: If the htmode is invalid.
        """
        if re.match(r"^[A-z0-9]+$", value) is None:
            raise ValueError("Invalid htmode")
        self.value = value


class Country(Attribute):
    """Object used to store the country of a device"""

    def __init__(self, value: str):
        """
        Initialize a Country object.

        Args:
            value (str): The country of the device.

        Raises:
            ValueError: If the country is invalid.
        """
        if re.match(r"^[A-Z]+$", value) is None:
            raise ValueError("Invalid Country")
        self.value = value


class Band(Attribute):
    """Object used to store the band of a device"""

    def __init__(self, value: str):
        """
        Initialize a Band object.

        Args:
            value (str): The band of the device.

        Raises:
            ValueError: If the band is invalid.
        """
        if re.match(r"^[a-z0-9]+$", value) is None:
            raise ValueError("Invalid Band")
        self.value = value


class Mode(Attribute):
    """Object used to store the mode of a wifi interface"""

    def __init__(self, value: str):
        """
        Initialize a Mode object.

        Args:
            value (str): The mode of the wifi interface.

        Raises:
            ValueError: If the mode is invalid.
        """
        if value not in ["sta", "ap", "adhoc", "monitor", "mesh"]:
            raise ValueError("Invalid Mode")
        self.value = value


class SSID(Attribute):
    """Object used to store the ssid of a wifi interface"""

    def __init__(self, ssid_prefix: str, ssid_suffix: str):
        """
        Initialize a SSID object.

        Args:
            ssid_prefix (str): The prefix of the SSID.
            ssid_suffix (str): The suffix of the SSID.

        Raises:
            ValueError: If the SSID is invalid.
        """
        value = ssid_prefix + ssid_suffix
        if re.match(r"^[A-z0-9_]{1,32}$", value) is None:
            raise ValueError("Invalid SSID")
        self.value = value


class Encryption(Attribute):
    """Object used to store the encryption of a wifi interface"""

    def __init__(self, value: str):
        """
        Initialize an Encryption object.

        Args:
            value (str): The encryption of the wifi interface.

        Raises:
            ValueError: If the encryption is invalid.
        """
        if value not in ["none", "wep", "psk", "psk2", "psk-mixed", "sae"]:
            raise ValueError("Invalid Encryption")
        self.value = value


class WifiPassphrase(Attribute):
    """Object used to store the key of a wifi interface
    
    """

    def __init__(self, value: str):
        """
        Initialize a Key object.

        Args:
            value (str): The key of the wifi interface.

        Raises:
            ValueError: If the key is invalid.
        """
        if re.match(r"^[\x21-\x7E]{8,63}$", value) is None:
            raise ValueError("Invalid Key")
        self.value = value


class UCIWifiDevice(UCIConfig):
    """Used to create a wireless interface
    See https://openwrt.org/docs/guide-user/network/wifi/basic#wi-fi_devices
    """

    path: Path
    type: WifiDeviceType
    channel: int
    htmode: Htmode
    country: Country
    band: Band
    disabled: int

    def __init__(
        self,
        name: UCISectionName,
        path: Path,
        device_type: WifiDeviceType,
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

        Raises:
            ValueError: If any of the arguments are invalid.
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
uci set wireless.{self}.disabled='{self.disabled}'
"""
        return string


class UCIWifiIface(UCIConfig):
    """Used to create a wireless interface
    See https://openwrt.org/docs/guide-user/network/wifi/basic#wi-fi_interfaces
    """

    def __init__(
        self,
        unetid: UNetId,
        device: UCIWifiDevice,
        network: UCIInterface,
        mode: Mode,
        ssid: SSID,
        encryption: Encryption,
        passphrase: WifiPassphrase,
        disabled: int = 0,
    ):
        """Create a wifi interface with password and SSID

        Args:
            unetid (UNetId): UNetId of the attached user
            device (UCIWifiDevice): WIfi device to attach to
            network (UCIInterface): Network to attach to (lan, wan, ...)
            mode (Mode): mostly ap
            ssid (SSID): SSID of the wifi
            encryption (Encryption): Type of encryption (none, wep, psk, psk2, psk-mixed, sae)
            passphrase (WifiPassphrase): Password of the wifi 8-63 characters printable ASCII
            disabled (int, optional): Is the iface disabled ?. Defaults to 0.
        """
        super().__init__(f"wifi_{unetid}_{device}")
        self.device = device
        self.network = network
        self.mode = mode
        self.ssid = ssid
        self.encryption = encryption
        self.key = passphrase
        self.disabled = disabled

    def uci_build_string(self):
        string = f"""uci set wireless.{self}=wifi-iface
uci set wireless.{self}.device='{self.device}'
uci set wireless.{self}.network='{self.network}'
uci set wireless.{self}.mode='{self.mode}'
uci set wireless.{self}.ssid='{self.ssid}'
uci set wireless.{self}.encryption='{self.encryption}'
uci set wireless.{self}.key='{self.key}'
uci set wireless.{self}.disabled='{self.disabled}'
"""
        return string

# ---------------------------------------------------------------------------- #
#                                   Firewall                                   #
# ---------------------------------------------------------------------------- #
class Description(Attribute):
    """Object used to store the description of a firewall rule"""

    def __init__(self, value: str):
        """
        Initialize a Description object.

        Args:
            value (str): The description value.

        Raises:
            ValueError: If the description value is invalid.
        """
        if re.match(r"^[A-z0-9_\- ]+$", value) is None:
            raise ValueError("Invalid Description")
        self.value = value


class TCPUDPPort(Attribute):
    """Object used to store the port of a firewall rule"""

    def __init__(self, value: int):
        """
        Initialize a TCPUDPPort object.

        Args:
            value (int): The port value.

        Raises:
            ValueError: If the port value is invalid.
        """
        if value < 0 or value > 65535:
            raise ValueError("Invalid Port")
        self.value = str(value)


class Protocol(Attribute):
    """Object used to store the protocol of a firewall rule"""

    def __init__(self, value: str = "tcp"):
        """
        Initialize a Protocol object.

        Args:
            value (str, optional): The protocol value. Defaults to "tcp".

        Raises:
            ValueError: If the protocol value is invalid.
        """
        if value not in ["tcp", "udp", "udplite", "icmp", "ah", "esp", "sctp", "all"]:
            raise ValueError("Invalid Protocol")
        self.value = value


class InOutForw(Attribute):
    """Object used to store the in/out/forward of a firewall zone"""

    def __init__(self, value: str = "ACCEPT"):
        """
        Initialize an InOutForw object.

        Args:
            value (str, optional): The in/out/forward value. Defaults to "ACCEPT".

        Raises:
            ValueError: If the in/out/forward value is invalid.
        """
        if value not in ["ACCEPT", "REJECT", "DROP"]:
            raise ValueError("Invalid In/Out/Forward")
        self.value = value


class Target(Attribute):
    """Object used to store the target of a firewall rule"""

    def __init__(self, value: str = "ACCEPT"):
        """
        Initialize a Target object.

        Args:
            value (str, optional): The target value. Defaults to "ACCEPT".

        Raises:
            ValueError: If the target value is invalid.
        """
        if value not in ["ACCEPT", "REJECT", "DROP", "MARK", "NOTRACK"]:
            raise ValueError("Invalid Target")
        self.value = value


class Family(Attribute):
    """Object used to store the family of a firewall rule"""

    def __init__(self, value: str = "ipv4"):
        """
        Initialize a Family object.

        Args:
            value (str, optional): The family value. Defaults to "ipv4".

        Raises:
            ValueError: If the family value is invalid.
        """
        if value not in ["ipv4", "ipv6", "any"]:
            raise ValueError("Invalid Family")
        self.value = value


class UCIFirewallDefaults(UCIConfig):
    """Used to create a default firewall configuration
    See https://openwrt.org/docs/guide-user/firewall/firewall_configuration#defaults
    """

    def __init__(self):
        """
        Initialize a UCIFirewallDefaults object.
        """
        super().__init__("defaults")

    def uci_build_string(self):
        """
        Build the UCI string representation of the defaults configuration.

        Returns:
            str: The UCI string representation of the defaults configuration.
        """
        string = f"""uci set firewall.{self}=defaults
uci set firewall.{self}.syn_flood='1'
uci set firewall.{self}.flow_offloading='1'
uci set firewall.{self}.flow_offloading_hw='1'
uci set firewall.{self}.input='ACCEPT'
uci set firewall.{self}.output='ACCEPT'
uci set firewall.{self}.forward='REJECT'
"""
        return string


class UCIRedirect4(UCIConfig):
    """Used to create a port redirection
    See https://openwrt.org/docs/guide-user/firewall/firewall_configuration#redirects
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
        src_dport: TCPUDPPort,
        dest: UCIInterface,
        dest_ip: IPAddress,
        dest_port: TCPUDPPort,
        proto: Protocol,
        src_ip: IPAddress = None,
    ):
        """
        Initialize a UCIRedirect4 object.

        Args:
            unetid (UNetId): The UNetId object.
            name (UCISectionName): The name of the redirect.
            desc (Description): The description of the redirect.
            src (UCIInterface): The source interface.
            src_ip (IPAddress): The source IP address.
            src_dport (TCPUDPPort): The source destination port.
            dest (UCIInterface): The destination interface.
            dest_ip (IPAddress): The destination IP address.
            dest_port (TCPUDPPort): The destination port.
            proto (Protocol): The protocol.
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
        """
        Build the UCI string representation of the redirect.

        Returns:
            str: The UCI string representation of the redirect.
        """
        string = f"""uci set firewall.{self}=redirect
uci set firewall.{self}.name='{self.desc}'
uci set firewall.{self}.target='DNAT'
uci set firewall.{self}.src='{self.src}'
uci set firewall.{self}.src_dport='{self.src_dport}'
uci set firewall.{self}.dest='{self.dest}'
uci set firewall.{self}.dest_ip='{self.dest_ip}'
uci set firewall.{self}.dest_port='{self.dest_port}'
"""
        if self.src_ip is not None:
            string += f"""uci set firewall.{self}.src_ip='{self.src_ip}'
"""
        return string


class UCIForwarding(UCIConfig):
    """Used to create a port forwarding
    See https://openwrt.org/docs/guide-user/firewall/firewall_configuration#forwardings
    """

    def __init__(self, src: UCIInterface, dest: UCIInterface):
        """
        Initialize a UCIForwarding object.

        Args:
            src (UCIInterface): The source interface.
            dest (UCIInterface): The destination interface.
        """
        super().__init__(f"forwarding_{src}_{dest}")
        self.src = src
        self.dest = dest

    def uci_build_string(self):
        """
        Build the UCI string representation of the forwarding.

        Returns:
            str: The UCI string representation of the forwarding.
        """
        string = f"""uci set firewall.{self}=forwarding
uci set firewall.{self}.src='{self.src}'
uci set firewall.{self}.dest='{self.dest}'
"""
        return string


class UCIZone(UCIConfig):
    """Used to create a firewall zone
    See https://openwrt.org/docs/guide-user/firewall/firewall_configuration#zones
    """

    def __init__(
        self,
        network: UCIInterface,
        _input: InOutForw,
        output: InOutForw,
        forward: InOutForw,
    ):
        """
        Initialize a UCIZone object.

        Args:
            network (UCIInterface): The network interface.
            _input (InOutForw): The input value.
            output (InOutForw): The output value.
            forward (InOutForw): The forward value.
        """
        super().__init__(f"zone_{network}")
        self.network = network
        self.input = _input
        self.output = output
        self.forward = forward

    def uci_build_string(self):
        """
        Build the UCI string representation of the zone.

        Returns:
            str: The UCI string representation of the zone.
        """
        string = f"""uci set firewall.{self}=zone
uci set firewall.{self}.name='{self}'
uci set firewall.{self}.network='{self.network}'
uci set firewall.{self}.input='{self.input}'
uci set firewall.{self}.output='{self.output}'
uci set firewall.{self}.forward='{self.forward}'
"""
        return string


class UCIRule(UCIConfig):
    """Used to create a firewall rule
    See https://openwrt.org/docs/guide-user/firewall/firewall_configuration#rules
    """
    desc: Description
    proto: Protocol
    src: UCIInterface
    src_ip: IPAddress
    src_port: TCPUDPPort
    dest: UCIInterface
    dest_ip: IPAddress
    dest_port: TCPUDPPort
    target: Target
    icmp_type: str
    family: Family

    def __init__(
        self,
        unetid: UNetId,
        name: UCISectionName,
        desc: Description,
        proto: Protocol,
        target: Target,
        src: UCIInterface = None,
        src_ip: IPAddress = None,
        src_port: TCPUDPPort = None,
        dest_ip: IPAddress = None,
        dest: UCIInterface = None,
        dest_port: TCPUDPPort = None,
        icmp_type: str = None,
        family: Family = "ipv4",
    ):
        """
        Initialize a UCIRule object.

        Args:
            unetid (UNetId): The UNetId object.
            name (UCISectionName): The name of the rule.
            desc (Description): The description of the rule.
            dest_ip (IPAddress): The destination IP address.
            dest (UCIInterface): The destination interface.
            proto (Protocol): The protocol.
            target (Target): The target.
            src (UCIInterface, optional): The source interface. Defaults to None.
            src_ip (IPAddress, optional): The source IP address. Defaults to None.
            src_port (TCPUDPPort, optional): The source port. Defaults to None.
            dest_port (TCPUDPPort, optional): The destination port. Defaults to None.
            family (Family, optional): The IP family. Defaults to "ipv4".
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
        self.icmp_type = icmp_type
        self.family = family

    def uci_build_string(self):
        """
        Build the UCI string representation of the rule.

        Returns:
            str: The UCI string representation of the rule.
        """
        string = f"""uci set firewall.{self}=rule
uci set firewall.{self}.name='{self.desc}'
uci set firewall.{self}.proto='{self.proto}'
uci set firewall.{self}.target='{self.target}'
uci set firewall.{self}.family='{self.family}'
"""
        if self.src is not None:
            string += f"""uci set firewall.{self}.src='{self.src}'
"""
        if self.src_ip is not None:
            string += f"""uci set firewall.{self}.src_ip='{self.src_ip}'
"""
        if self.src_port is not None:
            string += f"""uci set firewall.{self}.src_port='{self.src_port}'
"""
        if self.dest is not None:
            string += f"""uci set firewall.{self}.dest='{self.dest}'
"""
        if self.dest_ip is not None:
            string += f"""uci set firewall.{self}.dest_ip='{self.dest_ip}'
"""
        if self.dest_port is not None:
            string += f"""uci set firewall.{self}.dest_port='{self.dest_port}'
"""
        if self.icmp_type is not None:
            string += f"""uci set firewall.{self}.icmp_type='{self.icmp_type}'
"""
        return string


class UCISnat(UCIConfig):
    """Used to create a NAT rule
    See https://openwrt.org/docs/guide-user/firewall/firewall_configuration#source_nat
    """

    def __init__(
        self,
        wan_interface: UCIInterface,
        lan_interface: UCIInterface,
    ):
        """
        Initialize a UCISNat object.

        Args:
            wan_interface (UCIInterface): The WAN interface.
            lan_interface (UCIInterface): The LAN interface.
        """
        super().__init__(f"nat_{lan_interface}_to_{wan_interface}")
        self.wan_interface = wan_interface
        self.lan_interface = lan_interface
        self.lan_network = IPNetwork(f"{lan_interface.ip}/{lan_interface.mask}").network

    def uci_build_string(self):
        """
        Build the UCI string representation of the NAT rule.

        Returns:
            str: The UCI string representation of the NAT rule.
        """
        string = f"""uci set firewall.{self}=nat
uci set firewall.{self}.name='{self}'
uci set firewall.{self}.target='SNAT'
uci set firewall.{self}.snat_ip='{self.wan_interface.ip}'
uci set firewall.{self}.src='{self.lan_interface}'
uci set firewall.{self}.src_ip='{self.lan_network}'
uci set firewall.{self}.proto='all'
"""

        return string

# ---------------------------------------------------------------------------- #
#                                     DHCP                                     #
# ---------------------------------------------------------------------------- #
class DnsServers(Attribute):
    """Object used to store the DNS servers served by a DHCP server
    Its value is a list of IP addresses 
    """

    def __init__(self, value: list[IPAddress]):
        """
        Initialize the DnsServers object.

        Parameters:
        - value (list[IPAddress]): A list of IP addresses representing the DNS servers.

        Raises:
        - ValueError: If any of the IP addresses in the list is not of type IPAddress.
        """
        for ip in value:
            if not isinstance(ip, IPAddress):
                raise ValueError("Invalid DNS Servers")
        self.value = value


class UCIdnsmasq(UCIConfig):
    """Used to create a DNS server
    See https://openwrt.org/docs/guide-user/base-system/dhcp#common_options
    """

    dns_servers: DnsServers

    def __init__(self, dns_servers: DnsServers):
        """
        Initialize the UCIdnsmasq object.

        Parameters:
        - dns_servers (DnsServers): An instance of the DnsServers 
        class representing the DNS servers.

        Raises:
        - None
        """
        super().__init__("dnsmasq")
        self.dns_servers = dns_servers

    def uci_build_string(self):
        """
        Build the UCI configuration string for the UCIdnsmasq object.

        Returns:
        - string (str): The UCI configuration string.

        Raises:
        - None
        """
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
uci set dhcp.{self}.ednspacket_max='1232'
"""
        for dns in self.dns_servers.value:
            string += f"""uci add_list dhcp.{self}.server='{dns}'
"""
        return string


class UCIodchp(UCIConfig):
    """Used to create a DHCP server"""

    def __init__(self, loglevel: int = 4):
        """
        Initialize the UCIodchp object.

        Parameters:
        - loglevel (int): The log level for the DHCP server.

        Raises:
        - None
        """
        super().__init__("odhcpd")
        self.loglevel = loglevel

    def uci_build_string(self):
        """
        Build the UCI configuration string for the UCIodchp object.

        Returns:
        - string (str): The UCI configuration string.

        Raises:
        - None
        """
        string = f"""uci set dhcp.{self}=odhcpd
uci set dhcp.{self}.maindhcp='0'
uci set dhcp.{self}.leasefile='/tmp/hosts/odhcpd'
uci set dhcp.{self}.leasetrigger='/usr/sbin/odhcpd-update'
uci set dhcp.{self}.loglevel='{self.loglevel}'
"""
        return string


class UCIDHCP(UCIConfig):
    """Used to create a DHCP server
    See https://openwrt.org/docs/guide-user/base-system/dhcp#dhcp_pools
    """

    def __init__(self, interface: UCIInterface, start: int, limit: int, leasetime: int):
        """
        Initialize the UCIDHCP object.

        Parameters:
        - interface (UCIInterface): An instance of the UCIInterface 
        class representing the DHCP interface.
        - start (int): The starting IP address for the DHCP range.
        - limit (int): The maximum number of IP addresses in the DHCP range.
        - leasetime (int): The lease time for the DHCP addresses.

        Raises:
        - None
        """
        super().__init__(f"dhcp_{interface}")
        self.interface = interface
        self.start = start
        self.limit = limit
        self.leasetime = leasetime

    def uci_build_string(self):
        """
        Build the UCI configuration string for the UCIDHCP object.

        Returns:
        - string (str): The UCI configuration string.

        Raises:
        - None
        """
        string = f"""uci set dhcp.{self}=dhcp
uci set dhcp.{self}.interface='{self.interface}'
uci set dhcp.{self}.start='{self.start}'
uci set dhcp.{self}.limit='{self.limit}'
uci set dhcp.{self}.leasetime='{self.leasetime}'
"""
        return string

# ---------------------------------------------------------------------------- #
#                                   Dropbear                                   #
# ---------------------------------------------------------------------------- #

class UCIDropbear(UCIConfig):
    """Used to create a Dropbear configuration"""

    def __init__(self):
        """
        Initialize the UCIDropbear object.

        Parameters:
        - None

        Raises:
        - None
        """
        super().__init__("dropbear")

    def uci_build_string(self):
        """
        Build the UCI configuration string for the UCIDropbear object.

        Returns:
        - string (str): The UCI configuration string.

        Raises:
        - None
        """
        string = f"""uci set dropbear.{self}=dropbear
uci set dropbear.{self}.PasswordAuth='off'
uci set dropbear.{self}.RootPasswordAuth='off'
uci set dropbear.{self}.Port='22'
"""
        return string
