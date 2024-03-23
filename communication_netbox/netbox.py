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
    
    def __get_map_wlan_tag_to_ssid(self, all_interfaces) :
        """return a dict mapping the tag of a wlan to its ssid"""
        map_tag_to_ssid = {}
        wlans = [inter for inter in all_interfaces if inter['wireless_lans']]
        wlan_of_owner = [wlan for wlan in wlans if not wlan['tags']]
        if len(wlan_of_owner) != 1 :
            raise ValueError("There should exactly one wlan without tags" 
                             + " but there are " + str(len(wlan_of_owner)) + " wlans without tags")
        else :
            map_tag_to_ssid["box owner"] = wlan_of_owner[0]['wireless_lans'][0]['ssid']
            for wlan in wlans :
                if wlan['tags'] :
                    map_tag_to_ssid[wlan['tags'][0]['name']] = wlan['wireless_lans'][0]['ssid']
        return map_tag_to_ssid
        
    def __extract_ip_addresses(self, json_data) :
        """extract the ip adresses from a dict returned by Netbox containing
        the interfaces of a certain mac address
        Returns a list of dict {name : string, ip_addresses : []}"""
        all_interfaces = json_data['data']['interface_list']
        map_wlan_tag_to_ssid = self.__get_map_wlan_tag_to_ssid(all_interfaces)
        result = {ssid : [] for ssid in map_wlan_tag_to_ssid.values()}
        interfaces_with_ip_addresses = [interface for interface in 
                                     all_interfaces if interface['ip_addresses']]
        for interface in interfaces_with_ip_addresses :
            for ip_wrapper in interface['ip_addresses'] :#ip_wrapper is a dict containing the address and the tags
                infos = {"name": interface['name'], "ip_address": ip_wrapper['address']}
                tags = [tag['name'] for tag in ip_wrapper['tags']]
                wlan_tag = next((tag for tag in tags if tag in map_wlan_tag_to_ssid), "box owner")
                result[map_wlan_tag_to_ssid[wlan_tag]].append(infos)
        return result

    def get_infos_by_mac(self, mac : str) :
        """get the ip addresses associated with a mac address"""
        json_data = self.get_raw_infos_by_mac(mac)
        ip_addresses = self.__extract_ip_addresses(json_data)
        return ip_addresses
    

if __name__ == "__main__" :
    netbox = NetboxInterface()
    mac_address1 = "88:C3:97:14:B9:1F" #MAC address of a box in netbox.dev.fai.rezel.net
    mac_address2 = "88:C3:97:69:96:69"
    json_data = netbox.get_raw_infos_by_mac(mac=mac_address1)
    all_interfaces = json_data['data']['interface_list']
    # print(json.dumps(netbox._NetboxInterface__get_map_wlan_tag_to_ssid(all_interfaces), indent=4))
    # print(json.dumps(json_data, indent=4))
    print(json.dumps(netbox.get_infos_by_mac(mac_address1), indent=4))