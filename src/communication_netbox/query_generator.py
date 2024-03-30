"""
A few clients were considered :
* gql : doesn't allow the generation of query strings
* graphql-query : almost no documentation
* sgqlc : allows the generation of query strings, last commit 9 months ago but 489 stars
PLUS : exhaustive documentation : https://sgqlc.readthedocs.io/en/latest/

It is possible to test the queries in the playground of the Netbox GraphQL API :
http://netbox.dev.fai.rezel.net/graphql/
"""

from sgqlc.types import Type, Field, list_of
from sgqlc.operation import Operation


# Declaration of the data types corresponding to the GraphQL schema of Netbox 
#(only the types needed for the queries are declared)


class Tag(Type):
    """A tag is a label that can be attached to any object in Netbox

    Args:
        Type (Type): MotherClass to create type of objects in Netbox"""

    name = str


class NatIpAddressType(Type):
    """WARNING : THIS IS NOT A REAL TYPE IN THE GRAPHQL SCHEMA OF NETBOX
    It is used to represent the nat_inside field of the IpAddressType

    Args:
        Type (Type): MotherClass to create type of objects in Netbox"""
    address = str

class IpAddressType(Type):
    """IP address in Netbox

    Args:
        Type (Type): MotherClass to create type of objects in Netbox"""

    address = str
    nat_inside = NatIpAddressType
    tags = list_of(Tag)


class WirelessLAN(Type):
    """Wireless LAN in Netbox

    Args:
        Type (Type): MotherClass to create type of objects in Netbox"""

    ssid = str
    auth_psk = str


class Service(Type):
    """Service in Netbox

    Args:
        Type (Type): MotherClass to create type of objects in Netbox"""
    tags = list_of(Tag)
    ipaddresses = list_of(IpAddressType)
    ports = list_of(int)
    custom_field_data = str

class Device(Type):
    """Device in Netbox

    Args:
        Type (Type): MotherClass to create type of objects in Netbox"""
    services = list_of(Service)

class Interface(Type):
    """Interface in Netbox (can be a physical interface or a virtual one like a VLAN)

    Args:
        Type (Type): MotherClass to create type of objects in Netbox"""
    name = str
    tags = list_of(Tag)
    device = Device
    ip_addresses = list_of(IpAddressType)
    wireless_lans = list_of(WirelessLAN)

class Query(Type):
    """encompasses all the queries that can be made on the Netbox API

    Args:
        Type (Type): MotherClass to create type of objects in Netbox"""
    ip_address = Field(IpAddressType, args={"id":int})
    interface_list = Field(list_of("Interface"), args={"mac_address": str})


def camel_to_snake(string: str):
    """convert a camelCase string to snake_case while preserving
      the integrity of the MAC addresses in the string

    Args :
        string (str) : the string to convert to snake_case"""
    result = []
    is_previous_previous_colon = False
    is_previous_colon = False
    for c in string[1:]:
        if c.isupper() and not is_previous_colon and not is_previous_previous_colon:
            result.append("_")
            result.append(c.lower())
        else:
            is_previous_previous_colon = is_previous_colon
            is_previous_colon = c == ":"
            result.append(c)
    return string[0] + "".join(result)


def create_query_interface(mac: str) -> str:
    """create a query string to get the informations about a box from its MAC address

    Args :
        mac (str) : the MAC address of the box"""
    query = Operation(Query)
    interfaces = query.interface_list(mac_address=mac)
    # selection of the fields to be returned
    interfaces.name()
    interfaces.tags()
    interfaces.ip_addresses()
    interfaces.ip_addresses.address()
    interfaces.ip_addresses.nat_inside()
    interfaces.ip_addresses.nat_inside.address()
    interfaces.ip_addresses.tags()
    interfaces.ip_addresses.tags.name()
    interfaces.wireless_lans()
    interfaces.wireless_lans.ssid()
    interfaces.wireless_lans.auth_psk()
    interfaces.device()
    interfaces.device.services()
    interfaces.device.services.ipaddresses()
    interfaces.device.services.ports()
    interfaces.device.services.custom_field_data()
    # Netbox API understands snake_case but the sgqlc library uses camelCase for the fields
    # so we convert it
    snakified_query = camel_to_snake(str(query))
    return snakified_query

def create_query_ip(ip_id : int) :
    """create a query string to get the ip address bearing a certain IP

    Args :
        id (int) : id of the ip"""
    query = Operation(Query)
    ip_address = query.ip_address(id = ip_id)
    ip_address.address()
    snakified_query = camel_to_snake(str(query))
    return snakified_query
