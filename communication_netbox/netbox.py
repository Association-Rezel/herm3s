from query_generator import create_query
import requests
import json
import env


class NetboxInterface:
    """Permet de récupérer des informations sur les box dans Netbox,
    depuis son API GraphQL."""

    def __init__(self):
        self.__url = "http://netbox.dev.fai.rezel.net/graphql/"
        self.__token = env.TOKEN_NETBOX
        self.__headers = {
            'Authorization': 'Token ' + self.__token,
            'Accept': 'application/json',
        }
    
    def __request_netbox(self, query : str) :
        """execute query contre l'API GraphQL de Netbox, et retourne la réponse"""
        json_data = {
            'query': 'query ' + query,
        }
        response = requests.get(url=self.__url,
                                 headers=self.__headers,
                                 json=json_data)
        return response.json()
    
    def get_raw_infos_by_mac(self, mac : str) : 
        query = create_query(mac)
        return self.__request_netbox(query)
    
    def __extract_ip_addresses(self, json_data) :
        """extrait les adresses ip d'un json retourné par Netbox contenant
        les interfaces d'une certaine adresse mac
        Renvoie une liste de dict {name, ip_address}"""
        all_interfaces = json_data['data']['interface_list']
        interfaces_with_ip_adress = [interface for interface in 
                                     all_interfaces if interface['ip_addresses']]
        return [{'name': inter['name'], 'ip_address': inter['ip_addresses'][0]['address']}
                 for inter in interfaces_with_ip_adress]

    def get_ip_addresses_by_mac(self, mac : str) :
        """Récupère les adresses IP associées à une adresse MAC"""
        json_data = self.get_raw_infos_by_mac(mac)
        ip_addresses = self.__extract_ip_addresses(json_data)
        return ip_addresses
    

if __name__ == "__main__" :
    netbox = NetboxInterface()
    mac_adress1 = "88:C3:97:14:B9:1F" #adresse MAC de la box dans le netbox de test
    mac_adress2 = "88:C3:97:69:96:69"
    print(netbox.get_ip_addresses_by_mac(mac=mac_adress2))