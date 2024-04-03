"""
Define a class NetboxInterface to get :
* ssid of wlans
* ip adresses by ssid
* password by ssid

unet_id : user network id
"""

import json
import requests
import env

from utils import str_to_protocol
from query_generator import create_query_interface, create_query_ip

class NetboxInterface:
    """Gets informations from Netbox using its GraphQL API"""

    def __init__(self):
        self.__url = "http://netbox.dev.fai.rezel.net/graphql/"
        self.__token = env.TOKEN_NETBOX
        self.__headers = {
            "Authorization": "Token " + self.__token,
            "Accept": "application/json",
        }

    def __extract_unet_id_from_ssid(self, ssid: str):
        """extract the user network id from the ssid

        Args :
            ssid (str) : ssid of the wlan"""
        return ssid.split("-")[1]

    def __request_netbox(self, query: str):
        """execute query against the Netbox Graphql API and returns the result as a dict

        Args :
            query (str) : query execute against GraphQL API"""
        json_data_to_send = {
            "query": "query " + query,
        }
        response = requests.get(
            url=self.__url,
            headers=self.__headers,
            json=json_data_to_send,
            timeout=999999,
        )
        return response.json()

    def get_raw_infos_by_mac(self, mac: str):
        """Return the informations contained by Netbox related to the mac

        Args :
            mac (str) : mac address of the box
        """
        query = create_query_interface(mac)
        return self.__request_netbox(query)

    def __get_ip_by_id(self, ip_id: int):
        """Return the ip address bearing a certain id

        Args :
            ip_id (int) : id of the ip address"""
        query = create_query_ip(ip_id)
        raw_infos = self.__request_netbox(query)
        return raw_infos["data"]["ip_address"]["address"]

    def __get_map_wlan_tag_to_ssid(self, all_interfaces_list):
        """return a dict mapping the tag of a wlan to its ssid

        Args :
            all_interfaces_list (list) : list of all the interfaces associated
                with a given mac in Netbox"""
        map_tag_to_ssid = {}
        wlans = [inter for inter in all_interfaces_list if inter["wireless_lans"]]
        wlan_of_owner = [wlan for wlan in wlans if not wlan["tags"]]
        if len(wlan_of_owner) != 1:
            raise ValueError(
                "There should exactly one wlan without tags"
                + " but there are "
                + str(len(wlan_of_owner))
                + " wlans without tags"
            )
        map_tag_to_ssid["box owner"] = wlan_of_owner[0]["wireless_lans"][0]["ssid"]
        for wlan in wlans:
            if wlan["tags"]:
                ssid = wlan["wireless_lans"][0]["ssid"]
                map_tag_to_ssid[wlan["tags"][0]["name"]] = ssid
        return map_tag_to_ssid

    def __extract_psks(self, received_json_data):
        """return a dict mapping ssid to password (psk)"""
        all_interfaces_list = received_json_data["data"]["interface_list"]
        wlans = [
            inter["wireless_lans"][0]
            for inter in all_interfaces_list
            if inter["wireless_lans"]
        ]
        return {wlan["ssid"]: wlan["auth_psk"] for wlan in wlans}

    def __extract_ip_addresses(self, received_json_data):
        """extract the ip adresses from a dict returned by Netbox containing
        the interfaces of a certain mac address

        Args :
            received_json_data (list) : raw data received from netbox"""
        all_interfaces_list = received_json_data["data"]["interface_list"]
        map_wlan_tag_to_ssid = self.__get_map_wlan_tag_to_ssid(all_interfaces_list)
        result = {ssid: [] for ssid in map_wlan_tag_to_ssid.values()}
        interfaces_with_ip_addresses = [
            interface
            for interface in all_interfaces_list
            if interface["ip_addresses"]
        ]
        for interface in interfaces_with_ip_addresses:
            # ip_wrapper is a dict containing the address and the tags
            for ip_wrapper in interface["ip_addresses"]:
                infos = {"name": interface["name"],
                         "ip_address": ip_wrapper["address"]}
                if ip_wrapper["nat_inside"] :
                    infos["nat_inside_ip"] = ip_wrapper["nat_inside"]["address"]
                tags = [tag["name"] for tag in ip_wrapper["tags"]]
                wlan_tag = next((tag for tag in tags if tag in map_wlan_tag_to_ssid),
                                "box owner")
                result[map_wlan_tag_to_ssid[wlan_tag]].append(infos)
        return result

    def __extract_pat_rules(self, received_json_data):
        """extract the PAT rules from a dict returned by Netbox containing
        the interfaces of a certain mac address

        Args :
            received_json_data (list) : raw data received from netbox"""
        all_interfaces_list = received_json_data["data"]["interface_list"]
        all_services = all_interfaces_list[0]["device"]["services"]
        result = []
        for service in all_services:
            #if all necessary fields for PAT are defined
            if service["custom_field_data"] and service["ipaddresses"] and service["ports"]:
                inside_infos = json.loads(service["custom_field_data"])
                inside_ip_id = inside_infos["inside_ip_address"]
                inside_ip_address = self.__get_ip_by_id(inside_ip_id)
                result.append({
                    "inside_ip": inside_ip_address,
                    "inside_port": inside_infos["inside_port"],
                    "outside_ip": service["ipaddresses"][0]["address"],
                    "outside_port": service["ports"][0],
                    "protocol": str_to_protocol(service["protocol"]),
                })
        return result

    def get_infos_by_mac(self, mac: str):
        """Return :
            - a dictionary mapping the user network id (unet_id) to a list of 
            ip addresses 
            - a dictionary mapping the user network id (unet_id) to the password
            - a list of PAT rules

        Args :
            - mac (str) : mac address of the mac"""
        received_json_data = self.get_raw_infos_by_mac(mac)
        ip_addresses = self.__extract_ip_addresses(received_json_data)
        psks = self.__extract_psks(received_json_data)
        pat_rules = self.__extract_pat_rules(received_json_data)
        #rename the keys of the dict
        for ssid in ip_addresses.keys():
            unet_id = self.__extract_unet_id_from_ssid(ssid)
            ip_addresses[unet_id] = ip_addresses.pop(ssid)
        for ssid in psks.keys():
            unet_id = self.__extract_unet_id_from_ssid(ssid)
            psks[unet_id] = psks.pop(ssid)
        return ip_addresses, psks, pat_rules



if __name__ == "__main__":
    netbox = NetboxInterface()
    # MAC address of a box in netbox.dev.fai.rezel.net
    MAC_ADDRESS1 = "88:C3:97:14:B9:1F"
    MAC_ADDRESS2 = "88:C3:97:69:96:69"
    # json_data = netbox.get_raw_infos_by_mac(mac=MAC_ADDRESS2)
    # all_interfaces = json_data["data"]["interface_list"]
    # print(json.dumps(netbox._NetboxInterface__get_map_wlan_tag_to_ssid(all_interfaces), indent=4))
    print(json.dumps(netbox.get_infos_by_mac(MAC_ADDRESS2), indent=4, default=str))
    # print(json.dumps(json_data, indent=4))
    # print(create_query_interface(MAC_ADDRESS2))
