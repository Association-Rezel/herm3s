"""
Defines Models for the database
"""

from pydantic import BaseModel, Field, List

class WanIpv4(BaseModel):
    """
    WanIpv4 Model
    """
    vlan: str
    ip: str

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
    password: str

class UnetFirewall(BaseModel):
    """
    UnetFirewall Model
    """
    ipv4_port_forwarding: List[str]
    ipv6_port_forwarding: List[str]

class UnetProfile(BaseModel):
    """
    UnetProfile Model
    """
    unet_id: str
    location: str
    network: UnetNetwork
    wifi: WifiDetails
    firewall: UnetFirewall

class WanVlanIpv4(BaseModel):
    """
    WanVlanIpv4 Model
    """
    vlan_ip: str
    ipv4_net: str
    ipv4_gateway: str

class WanVlanIpv6(BaseModel):
    """
    WanVlanIpv6 Model
    """
    vlan_ip: str
    ipv6_net: str
    ipv6_gateway: str

class Box(BaseModel):
    """
    Box Model
    """
    id: str = Field(None, alias='_id')
    type: str
    name: str
    mac : str
    unet: List[UnetProfile]
    wan_vlan: List[WanIpv4 | WanIpv6]
