"""
Defines classes to format the data received from the Netbox API
"""
from __future__ import annotations
from pydantic import BaseModel


class IpAddress(BaseModel):
    """Data model of :  IP address in Netbox"""
    address: str
    nat_inside: IpAddress | None = None
    custom_field_data: str = ""

class WirelessLAN(BaseModel):
    """Data model of :  Wireless LAN """
    id : int
    ssid: str
    auth_psk: str

class Service(BaseModel):
    """Data model of : Service"""
    name : str = ""
    ipaddresses: list[IpAddress]
    ports: list[int]
    protocol: str
    custom_field_data: str = ""

class Device(BaseModel):
    """Data model of : Device"""
    services: list[Service]

class Interface(BaseModel):
    """Data model of : Interface
    (can be a physical interface or a virtual one like a VLAN)"""
    name : str
    ip_addresses : list[IpAddress] = []
    wireless_lans : list[WirelessLAN] = []
    device : Device

class InterfaceResponse(BaseModel):
    """Data model of : Respnse from netbox when queried for interfaces"""
    interface_list : list[Interface]


class PATCustomField(BaseModel) :
    """Data model of : custom field of service PAT"""
    inside_port : int
    inside_ip_address : int

if __name__ == "__main__":
    test_json = """{
            "address": "137.194.9.34/22",
            "nat_inside": {
              "address": "192.168.2.0/24"
            },
            "tags": [
              {
                "name": "box-kley-666-wlan-2"
              }
            ]
          }"""
    ip = IpAddress.model_validate_json(test_json)
    print(ip)
