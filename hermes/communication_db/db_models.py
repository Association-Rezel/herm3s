"""
Defines Models for the database
"""

from pydantic import BaseModel, Field


REGEX_IPV4_CIDR = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/(?:[0-9]|[1-2][0-9]|3[0-2])$"
REGEX_IPV4 = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
REGEX_MAC = r"([0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5})"
REGEX_UNET_ID = r"^[a-z0-9]{8}$"


class WanIpv4(BaseModel):
    """
    WanIpv4 Model
    """

    vlan: str
    ip: str = Field(pattern=REGEX_IPV4_CIDR)


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

    address: str
    vlan: int


class UnetNetwork(BaseModel):
    """
    UnetNetwork Model
    """

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
    lan_ip: str = Field(pattern=REGEX_IPV4)
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

    unet_id: str = Field(pattern=REGEX_UNET_ID)
    network: UnetNetwork
    wifi: WifiDetails
    firewall: UnetFirewall


class WanVlan(BaseModel):
    """
    WanVlan Model
    """

    vlan_id: str
    ipv4_gateway: str = Field(pattern=REGEX_IPV4_CIDR + r"|^$")
    ipv6_gateway: str


class IdModel(BaseModel):
    """
    IdModel Model
    """

    oid: str = Field(alias="$oid")


class Box(BaseModel):
    """
    Box Model
    """

    id: str | IdModel | None = Field(alias="_id", default=None)
    type: str  # Type de box (ex: ac2350)
    main_unet_id: str = Field(pattern=REGEX_UNET_ID)
    mac: str = Field(pattern=REGEX_MAC)
    unets: list[UnetProfile]
    wan_vlan: list[WanVlan]
