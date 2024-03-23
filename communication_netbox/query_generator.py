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


"""Declaration of the data types corresponding to the GraphQL schema of Netbox
(only the types needed for the query are declared, although a few more are added
 to provide examples for future extensions)"""
class IpAddressType(Type):
    # id = int
    address = str

class Site(Type):
    id = int
    name = str

class Rack(Type):
    id = int
    name = str

class Device(Type):
    id = int
    name = str
    site = Field(Site)
    rack = Field(Rack)
    primary_ip4 = Field(IpAddressType)
    primary_ip6 = Field(IpAddressType)

class Interface(Type):
    id = int
    name = str
    mac_address = str
    ip_addresses = list_of(IpAddressType)
    device = Field(Device)

class Query(Type):
    device_list = Field(list_of('Device'), args={'role': str})
    interface_list = Field(list_of('Interface'), args={'mac_address': str})


def camel_to_snake(string : str):
    """convert a camelCase string to snake_case while preserving the integrity of the MAC addresses"""
    result = []
    is_previous_previous_colon = False
    is_previous_colon = False
    for c in string[1:] :
        if c.isupper() and not is_previous_colon and not is_previous_previous_colon:
            result.append('_')
            result.append(c.lower())
        else :
            is_previous_previous_colon = is_previous_colon
            is_previous_colon = (c == ':')
            result.append(c)
    return string[0] + ''.join(result)

def create_query(mac : str) -> str :
    """create a query string to get the informations about a box from its MAC address"""
    query = Operation(Query)
    interfaces = query.interface_list(mac_address=mac)
    #selection of the fields to be returned
    interfaces.name()
    interfaces.ip_addresses()
    #Netbox API understands snake_case but the sgqlc library uses camelCase for the fields
    # so we convert it
    snakified_query = camel_to_snake(str(query)) 
    return snakified_query