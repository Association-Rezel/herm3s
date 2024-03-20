"""
Différents clients considérés :
* gql : ne permet pas la génération de query string
* graphql-query : quasiment pas de doc
* sgqlc : permet la génération de query string, dernier commit il y a 9 mois mais 489 stars 
(et documentation exhaustive : https://sgqlc.readthedocs.io/en/latest/)

http://netbox.dev.fai.rezel.net/graphql/ pour le playground
"""

from sgqlc.types import Type, Field, list_of
from sgqlc.operation import Operation


"""On déclare les types de données correspondant au schéma GrahpQL de Netbox"""
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
    """Convertit une chaine de caractère de camelCase en snake_case en préservant les adresses MAC"""
    resultat = []
    is_previous_previous_colon = False
    is_previous_colon = False
    for c in string[1:] :
        if c.isupper() and not is_previous_colon and not is_previous_previous_colon:
            resultat.append('_')
            resultat.append(c.lower())
        else :
            is_previous_previous_colon = is_previous_colon
            is_previous_colon = (c == ':')
            resultat.append(c)
    return string[0] + ''.join(resultat)

def create_query(mac : str) -> str :
    """génère une query string pour récupérer les informations sur une box
      à partir de son adresse MAC"""
    query = Operation(Query)
    interfaces = query.interface_list(mac_address=mac)
    #sélection des champs à récupérer
    interfaces.name()
    interfaces.ip_addresses()
    #Netbox attend du snake_case et sgqlc génère du camelCase donc :
    snakified_query = camel_to_snake(str(query)) 

    return snakified_query