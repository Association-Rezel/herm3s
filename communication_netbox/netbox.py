from query_generator import create_query
import requests
import json
import env


class NetboxInterface:
    """Gets informations from Netbox using its GraphQL API"""

    def __init__(self):
        self.__url = "http://netbox.dev.fai.rezel.net/graphql/"
        self.__token = env.TOKEN_NETBOX
        self.__headers = {
            'Authorization': 'Token ' + self.__token,
            'Accept': 'application/json',
        }
    
    def __request_netbox(self, query : str) :
        """exectue query against the Netbox Graphql API and returns the result as a dict"""
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
        """extract the ip adresses from a dict returned by Netbox containing
        the interfaces of a certain mac address
        Returns a list of dict {name : string, ip_addresses : []}"""
        all_interfaces = json_data['data']['interface_list']
        interfaces_with_ip_addresses = [interface for interface in 
                                     all_interfaces if interface['ip_addresses']]
        return [{'name': inter['name'], 
                 'ip_address': [ip_wrapper['address'] for ip_wrapper in inter['ip_addresses']]}
                 for inter in interfaces_with_ip_addresses]

    def get_ip_addresses_by_mac(self, mac : str) :
        """get the ip addresses associated with a mac address"""
        json_data = self.get_raw_infos_by_mac(mac)
        ip_addresses = self.__extract_ip_addresses(json_data)
        return ip_addresses
    

if __name__ == "__main__" :
    netbox = NetboxInterface()
    mac_address1 = "88:C3:97:14:B9:1F" #MAC address of a box in netbox.dev.fai.rezel.net
    mac_address2 = "88:C3:97:69:96:69"
    print(netbox.get_ip_addresses_by_mac(mac=mac_address2))