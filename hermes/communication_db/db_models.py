"""
Defines Models for the database
"""

from pydantic import BaseModel, Field

REGEX_IPV4_MASK = r"^(((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4})\/(3[0-2]|[1-2]\d|\d)$"
REGEX_IPV4_NO_MASK = r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$"
REGEX_MAC = r"([0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5})"

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

    ipv4_portforwarding: list[Ipv4Portforwarding]
    ipv6_portopening: list[Ipv6Portopening]


class UnetProfile(BaseModel):
    """
    UnetProfile Model
    """

    unet_id: str = Field(pattern=r"^[a-z0-9]{8}$")
    network: UnetNetwork
    wifi: WifiDetails
    firewall: UnetFirewall


class WanVlanIpv4(BaseModel):
    """
    WanVlanIpv4 Model
    """

    vlan_id: str = Field(alias="id")
    ipv4_net: str = Field(pattern=REGEX_IPV4_MASK)
    ipv4_gateway: str = Field(pattern=REGEX_IPV4_NO_MASK)


class WanVlanIpv6(BaseModel):
    """
    WanVlanIpv6 Model
    """

    vlan_id: str = Field(alias="id")
    ipv6_net: str
    ipv6_gateway: str


class ObjectId(BaseModel):
    """
    ObjectId Model
    """

    id:str

class Box(BaseModel):
    """
    Box Model
    """

    id: ObjectId = Field(alias="_id")
    type: str  # type de box (ex: ac2350)
    mac: str = Field(pattern=REGEX_MAC)
    unets: list[UnetProfile]
    wan_vlan: list[WanIpv4 | WanIpv6] = Field(alias="wan-vlan")
