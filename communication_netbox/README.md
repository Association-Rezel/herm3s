# Communication avec netbox

Dans `query_generator.py` se trouve la modélisation d'une partie du schéma de la base de donnée de Netbox sous forme de classes Python. Cela permet de générer des query string (requêtes sous formes de chaines de caractères) à l'aide de sgqlc ([Simple GraqhQL Client](https://sgqlc.readthedocs.io/en/latest/))

Dans `netbox.py`, on définit la classe NetboxInterface qui fournit notamment la méthode `get_ip_addresses_by_mac` qui prend la mac d'une box en argument et qui renvoie la liste des adresses ip associées à cette mac dans Netbox sous la forme d'une liste de dict (ex : [{"name" : "eth0.65", "ip_address" : "8.8.8.8/24"}]).

Il faut encore :

- déterminer comment représenter une box avec plusieurs wifis dans netbox
- récupérer les noms des wifis
- récupérer la liste de toutes les ips pour chaque vlan
