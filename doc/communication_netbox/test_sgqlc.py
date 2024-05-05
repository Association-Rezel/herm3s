"""
Démonstration de l'utilisation du client GraphQL sgqlc pour interroger l'API de Netbox

Nathan Roos
09/03/2024
"""

# sgqlc = simple graphql client
from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.types import Type, Field, list_of
from sgqlc.operation import Operation
import re  # pour transformer les noms de champs de camelCase en snake_case
import json

url = "http://netbox.dev.fai.rezel.net/graphql/"
token_netbox = "91a0e80dd5c290ba0d7f7d070a9f3fd80a61e6ea"
headers = {
    "Authorization": "Token " + token_netbox,
    "Accept": "application/json",
}


def camel_to_snake(string: str):
    """Convertit une chaine de caractère de camelCase en snake_case"""
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    return pattern.sub("_", string).lower()


endpoint = HTTPEndpoint(url, headers)


# On déclare les types de données correspondant au schéma GrahpQL de Netbox
class IpAddressType(Type):
    id = int
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


class Query(Type):
    device_list = Field(list_of("Device"), args={"role": str})


# construction de la requête
query = Operation(Query)
devices = query.device_list(role="box")
devices.id()
devices.name()
devices.site()
# devices.rack()
devices.primary_ip4()
devices.primary_ip6()
# print(op)

snakified_query = camel_to_snake(str(query))
print("=======")
print("QUERY :")
print("=======")
print(snakified_query)


# execution de la requete et afficahe des données
data = endpoint(snakified_query)
print("\n==========")
print("RESULTAT :")
print("==========")
print(json.dumps(data, indent=4))
