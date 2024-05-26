"""
Defines classes to format the data received from the Netbox API
"""

from __future__ import annotations
from pydantic import BaseModel


class IpAddressCustomField(BaseModel):
    """Data model of :  custom field in IP address"""

    linked_wlan: int


class IpAddress(BaseModel):
    """Data model of :  IP address in Netbox"""

    address: str
    custom_field_data: IpAddressCustomField | None = None
    nat_inside: IpAddress | None = None


class WirelessLANCustomField(BaseModel):
    """Data model of :  custom field in Wireless LAN"""

    unet_id: str


class WirelessLAN(BaseModel):
    """Data model of :  Wireless LAN"""

    id: int
    ssid: str
    auth_psk: str
    custom_field_data: WirelessLANCustomField


class PFCustomField(BaseModel):
    """Data model of : custom field of service PF"""

    inside_port: int
    inside_ip_address: int
    PF_linked_WLAN: int


class Service(BaseModel):
    """Data model of : Service"""

    name: str = ""
    protocol: str
    ipaddresses: list[IpAddress]
    ports: list[int]
    custom_field_data: PFCustomField


class Device(BaseModel):
    """Data model of : Device"""

    services: list[Service]


class Interface(BaseModel):
    """Data model of : Interface
    (can be a physical interface or a virtual one like a VLAN)"""

    name: str
    ip_addresses: list[IpAddress] = []
    wireless_lans: list[WirelessLAN] = []
    device: Device


class InterfaceResponse(BaseModel):
    """Data model of : Response from netbox when queried for interfaces"""

    interface_list: list[Interface]
