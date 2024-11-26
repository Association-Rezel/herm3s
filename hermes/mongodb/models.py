"""
Defines Models for the database
"""

import logging
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from typing import Optional, Self

from pydantic import Field, field_validator, model_validator

from hermes.mongodb.base import PortableMac, RezelBaseModel

REGEX_UNET_ID = r"^[a-z0-9]{8}$"


class WanIpv4(RezelBaseModel):
    """
    WanIpv4 Model
    """

    vlan: int
    ip: IPv4Interface


class WanIpv6(RezelBaseModel):
    """
    WanIpv6 Model
    """

    vlan: int
    ip: IPv6Interface


class LanIpv4(RezelBaseModel):
    """
    LanIpv4 Model
    """

    address: IPv4Interface
    vlan: int


class UnetNetwork(RezelBaseModel):
    """
    UnetNetwork Model
    """

    wan_ipv4: WanIpv4
    wan_ipv6: WanIpv6
    ipv6_prefix: IPv6Network
    lan_ipv4: LanIpv4


class WifiDetails(RezelBaseModel):
    """
    WifiDetails Model
    """

    ssid: str
    psk: str


class Ipv4Portforwarding(RezelBaseModel):
    """
    Ipv4Portforwarding Model
    """

    wan_port: int = Field(ge=0, le=65535)
    lan_ip: IPv4Address
    lan_port: int = Field(ge=0, le=65535)
    protocol: str = Field(pattern=r"^(tcp|udp)$")
    name: str
    desc: str

    @field_validator("protocol", mode="before")
    @classmethod
    def protocol_upper(cls, v):
        return v.lower()


class Ipv6Portopening(RezelBaseModel):
    """
    Ipv6Portopening Model
    """

    ip: IPv6Address
    port: int = Field(ge=0, le=65535)
    protocol: str = Field(pattern=r"^(tcp|udp)$")
    name: str
    desc: str

    @field_validator("protocol", mode="before")
    @classmethod
    def protocol_upper(cls, v):
        return v.lower()


class UnetFirewall(RezelBaseModel):
    """
    UnetFirewall Model
    """

    ipv4_port_forwarding: list[Ipv4Portforwarding]
    ipv6_port_opening: list[Ipv6Portopening]


class DnsServers(RezelBaseModel):
    """
    DnsServers Model
    """

    ipv4: list[IPv4Address]
    ipv6: list[IPv6Address]


class Dhcp(RezelBaseModel):
    """
    DnsV4 Model
    """

    dns_servers: DnsServers


class UnetProfile(RezelBaseModel):
    """
    UnetProfile Model
    """

    unet_id: str = Field(pattern=REGEX_UNET_ID)
    network: UnetNetwork
    wifi: WifiDetails
    firewall: UnetFirewall
    dhcp: Dhcp

    @model_validator(mode="after")
    def _validate(self) -> Self:
        for ipv4_port_forwarding in self.firewall.ipv4_port_forwarding:
            if ipv4_port_forwarding.lan_ip not in self.network.lan_ipv4.address.network:
                logging.error("Failed to validate unet profile %s", self.unet_id)
                logging.error(
                    "Port forwarding error : %s is not in %s",
                    ipv4_port_forwarding.lan_ip,
                    self.network.lan_ipv4.address.network,
                )
                raise ValueError(
                    f"Port forwarding error : {ipv4_port_forwarding.lan_ip} is not in {self.network.lan_ipv4.address.network}"
                )

        for ipv6_port_opening in self.firewall.ipv6_port_opening:
            if ipv6_port_opening.ip not in self.network.ipv6_prefix:
                logging.error("Failed to validate unet profile %s", self.unet_id)
                logging.error(
                    "Port opening error : %s is not in %s",
                    ipv6_port_opening.ip,
                    self.network.ipv6_prefix,
                )
                raise ValueError(
                    f"Port opening error : {ipv6_port_opening.ip} is not in {self.network.ipv6_prefix}"
                )

        return self


class WanVlan(RezelBaseModel):
    """
    WanVlan Model
    """

    vlan_id: int
    ipv4_gateway: Optional[IPv4Address] = Field(None)
    ipv6_gateway: Optional[IPv6Address] = Field(None)


class Box(RezelBaseModel):
    """
    Box Model
    """

    type: str  # Type de box (ex: ac2350)
    main_unet_id: str = Field(pattern=REGEX_UNET_ID)
    mac: PortableMac
    unets: list[UnetProfile]
    wan_vlan: list[WanVlan]
