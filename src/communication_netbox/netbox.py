"""
Define a class NetboxInterface to get :
* ssid of wlans
* ip adresses by ssid
* password by ssid
"""

import json
import requests
import env

from query_generator import create_query


class NetboxInterface:
    """Gets informations from Netbox using its GraphQL API"""

    def __init__(self):
        self.__url = "http://netbox.dev.fai.rezel.net/graphql/"
        self.__token = env.TOKEN_NETBOX
        self.__headers = {
            "Authorization": "Token " + self.__token,
            "Accept": "application/json",
        }

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
        query = create_query(mac)
        return self.__request_netbox(query)

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
        Returns a list of dict {name : string, ip_addresses : []}

        Args :
            received_json_data (list) : raw data received from netbox"""
        all_interfaces_list = received_json_data["data"]["interface_list"]
        map_wlan_tag_to_ssid = self.__get_map_wlan_tag_to_ssid(all_interfaces_list)
        result = {ssid: [] for ssid in map_wlan_tag_to_ssid.values()}
        interfaces_with_ip_addresses = [
            interface
            for interface in all_interfaces
            if interface["ip_addresses"]
        ]
        for interface in interfaces_with_ip_addresses:
            # ip_wrapper is a dict containing the address and the tags
            for ip_wrapper in interface["ip_addresses"]:
                infos = {"name": interface["name"], "ip_address": ip_wrapper["address"]}
                tags = [tag["name"] for tag in ip_wrapper["tags"]]
                wlan_tag = next((tag for tag in tags if tag in map_wlan_tag_to_ssid),
                                "box owner")
                result[map_wlan_tag_to_ssid[wlan_tag]].append(infos)
        return result

    def get_infos_by_mac(self, mac: str):
        """get the ip addresses associated with a mac address

        Args :
            mac (str) : mac address of the mac"""
        received_json_data = self.get_raw_infos_by_mac(mac)
        ip_addresses = self.__extract_ip_addresses(received_json_data)
        return ip_addresses, self.__extract_psks(received_json_data)


if __name__ == "__main__":
    netbox = NetboxInterface()
    # MAC address of a box in netbox.dev.fai.rezel.net
    MAX_ADDRESS1 = "88:C3:97:14:B9:1F"  
    MAX_ADDRESS2 = "88:C3:97:69:96:69"
    json_data = netbox.get_raw_infos_by_mac(mac=MAX_ADDRESS2)
    all_interfaces = json_data["data"]["interface_list"]
    # print(json.dumps(netbox._NetboxInterface__get_map_wlan_tag_to_ssid(all_interfaces), indent=4))
    # print(json.dumps(json_data, indent=4))
    print(json.dumps(netbox.get_infos_by_mac(MAX_ADDRESS2), indent=4))
    # print(create_query(mac=MAX_ADDRESS2))
