"""
Defines Models for the database
"""

from pydantic import BaseModel, Field

REGEX_IPV4_MASK = (
    r"^(((25[0-5]|(2[0-4]|1[0-9]|[1-9]|)[0-9])\.?\b){4})\/(3[0-2]|[1-2][0-9]|[0-9])$"
)
REGEX_IPV4_NO_MASK = r"^((25[0-5]|(2[0-4]|1[0-9]|[1-9]|)[0-9])\.?\b){4}$"
REGEX_MAC = r"([0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5})"


class IpMask(BaseModel):
    """
    IpMask Model
    ex : {"ip": "0.0.0.0/8", "version": "ipv4"}
    """

    ip: str
    version: str


class IpNoMask(BaseModel):
    """
    IpNoMask Model
    ex: {"ip": "0.0.0.0", "version": "ipv4"}
    """

    ip: str
    version: str


class WanIpv4(BaseModel):
    """
    WanIpv4 Model
    """

    vlan: str
    ip: str = Field(pattern=REGEX_IPV4_MASK)


class WanIpv6(BaseModel):
    """
    WanIpv6 Model
    """

    vlan: str
    ip: str


class LanIpv4(BaseModel):
    """
    LanIpv4 Model
    """

    net: str


class UnetNetwork(BaseModel):
    """"""

    wan_ipv4: WanIpv4
    wan_ipv6: WanIpv6
    ipv6_prefix: str
    lan_ipv4: LanIpv4


class WifiDetails(BaseModel):
    """
    WifiDetails Model
    """

    ssid: str
    psk: str


class Ipv4Portforwarding(BaseModel):
    """
    Ipv4Portforwarding Model
    """

    wan_port: int
    lan_ip: str = Field(pattern=REGEX_IPV4_NO_MASK)
    lan_port: int
    protocol: str
    name: str
    desc: str


class Ipv6Portopening(BaseModel):
    """
    Ipv6Portopening Model
    """

    ip: str
    port: int
    protocol: str
    name: str
    desc: str


class UnetFirewall(BaseModel):
    """
    UnetFirewall Model
    """

    ipv4_port_forwarding: list[Ipv4Portforwarding]
    ipv6_port_opening: list[Ipv6Portopening]


class UnetProfile(BaseModel):
    """
    UnetProfile Model
    """

    unet_id: str = Field(pattern=r"^[a-z0-9]{8}$")
    network: UnetNetwork
    wifi: WifiDetails
    firewall: UnetFirewall


class NetGateway(BaseModel):
    """
    NetGateway Model : contains a network and the default gateway in it
    """

    net: IpMask
    gateway: IpNoMask


class WanVlan(BaseModel):
    """
    WanVlan Model
    """

    vlan_id: str
    net_gateway: list[NetGateway]


class Box(BaseModel):
    """
    Box Model
    """

    id: str = Field(alias="_id")
    type: str  # type de box (ex: ac2350)
    mac: str = Field(pattern=REGEX_MAC)
    unets: list[UnetProfile]
    wan_vlan: list[WanVlan]
