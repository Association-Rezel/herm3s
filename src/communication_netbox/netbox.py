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
# from pydantic import ValidationError #TO ADD WHEN THE ERRORS WILL BE HANDLED

#to avoid import error with communication_deamon
from netbox_data_models import InterfaceResponse, Interface, WirelessLAN, PATCustomField
from query_generator import create_query_interface, create_query_ip

# from netbox_data_models import InterfaceResponse, Interface, WirelessLAN, PATCustomField
# from query_generator import create_query_interface, create_query_ip



class NetboxInterface2:
    """Gets and validates informations from Netbox using its GraphQL API"""

    def __init__(self):
        self.__url = "http://netbox.dev.fai.rezel.net/graphql/"
        self.__token = env.TOKEN_NETBOX
        self.__headers = {
            "Authorization": "Token " + self.__token,
            "Accept": "application/json",
        }

    def __get_unet_id_from_ssid(self, ssid: str):
        """extract the user network id from the ssid of the wlan

        Args :
            ssid (str) : ssid of the wlan"""
        return ssid.split("-")[1]

    def __request_netbox(self, query: str) -> dict:
        """execute query against the Netbox Graphql API and returns the result as a dict

        Args :
            query (str) : query string"""
        json_data_to_send = {"query": "query " + query}
        timeout = 999999
        response = requests.get(
            url=self.__url,
            headers=self.__headers,
            json=json_data_to_send,
            timeout=timeout
        )
        return response.json()

    def __get_ip_by_id(self, ip_id: int) -> str:
        """Return the ip address bearing a certain id

        Args :
            ip_id (int) : id of the ip address"""
        query = create_query_ip(ip_id)
        raw_infos = self.__request_netbox(query)
        return raw_infos["data"]["ip_address"]["address"]

    def get_interfaces_by_mac(self, mac: str) -> list[Interface]:
        """Return a list of the interfaces linked to the mac"

        Args :
            mac (str) : mac address of the box
        """
        query = create_query_interface(mac)
        json_response = self.__request_netbox(query)
        #TODO : GESTION DES ERREURS DE VALIDATION
        interface_response : InterfaceResponse = InterfaceResponse.model_validate(json_response['data'])
        return interface_response.interface_list

    def __get_wlans(self, interfaces : list[Interface]) -> list[WirelessLAN]:
        """Return all the wireless LANs mentionned in interfaces
        
        Args :
            - interfaces (list[Interface]): list of all the interfaces with a given mac"""
        wlans = [inter.wireless_lans[0] for inter in interfaces if inter.wireless_lans]
        return wlans

    def _get_unet_ids(self, interfaces : list[Interface]) -> list[str] :
        """Return the UNet Ids contained in the list of interface
        
        Args :
            - interfaces (list[Interface]): list of all the interfaces with a given mac"""
        wlans = self.__get_wlans(interfaces)
        ssids = [wlan.ssid for wlan in wlans]
        unet_ids = [self.__get_unet_id_from_ssid(ssid) for ssid in ssids]
        return unet_ids

    def __get_ip_addresses(self, interfaces : list[Interface]) :
        """Return list of dict with the following keys :
        - "name" (name of the interface)
        - "ip_address"
        - "nat_inside_ip" (NAT address inside)
        
        Args :
            - interfaces (list[Interface]): list of all the interfaces with a given mac"""
        res = []
        interfaces_with_ip_addresses = [inter for inter in interfaces if inter.ip_addresses]
        for interface in interfaces_with_ip_addresses :
            for ip_wrapper in interface.ip_addresses :
                res.append({
                    "name" : interface.name,
                    "ip_address" : ip_wrapper.address,
                    "nat_inside_ip" : ip_wrapper.nat_inside.address if ip_wrapper.nat_inside else None
                })
        return res

    def __get_passwords(self, interfaces : list[Interface]) -> dict[str:str] :
        """return a dict binding each UNet Id to its wifi password
        
        Args :
            - interfaces (list[Interface]): list of all the interfaces with a given mac"""
        wlans : list[WirelessLAN] = self.__get_wlans(interfaces)
        return {
            self.__get_unet_id_from_ssid(wlan.ssid) : wlan.auth_psk
            for wlan in wlans
        }

    def __get_main_unet_id(self, interfaces : list[Interface]) -> str :
        """Return the UNet Id of the main user of the box (adhérent fibre)
        We assume that the main user uses "wlan0"
        
        Args :
            - interfaces (list[Interface]): list of all the interfaces with a given mac"""
        interfaces_named_wlan0 = [
            interface for interface in interfaces
            if interface.wireless_lans
            and interface.name == "wlan0"
        ]
        #TODO : traiter le cas d'erreur où il n'y a pas exactement un "wlan0"
        main_ssid = interfaces_named_wlan0[0].wireless_lans[0].ssid
        main_unet_id = self.__get_unet_id_from_ssid(main_ssid)
        return main_unet_id

    def __get_pat_rules(self, interfaces : list[Interface]) -> list[dict[str : str | int]] :
        """Return a list of dict(representing the pat rules) with keys :
        - "inside_ip" (ex: "192.168.0.0/24")
        - "inside_port": (ex: 25)
        - "outside_ip": (ex: "137.194.8.2/22")
        - "outside_port": (ex: 80),
        - "protocol": ("tcp" | "udp")

        Args :
            - interfaces (list[Interface]): list of all the interfaces with a given mac"""
        pat_rules : list[dict]= []
        services = interfaces[0].device.services
        pat_services = [s for s in services if s.name == "PAT" and s.custom_field_data]
        for s in pat_services :
            #TODO : check that there exactly one outside ip and port
            custom_fields = PATCustomField.model_validate_json(s.custom_field_data)
            pat_rules.append({
                "inside_ip" : self.__get_ip_by_id(str(custom_fields.inside_ip_address)),
                "inside_port" : custom_fields.inside_port,
                "outside_ip" : s.ipaddresses[0].address,
                "outside_port" : s.ports[0],
                "protocol" : s.protocol.lower()
            })
        return pat_rules

    def get_infos_by_mac(self, mac: str,
                         ip_adresses = True,
                         passwords = True,
                         pat_rules = True,
                         main_unet_id=True):
        """Return a dictionnary with keys :
        - "ip_addresses"
        - "passwords"
        - "pat_rules"
        - "main_unet_id"

        Args :
            mac (str) : mac address of the box
            ip_adresses (bool) : if True, return the ip adresses by unet_id
            passwords (bool) : if True, return the passwords by unet_id
            pat_rules (bool) : if True, return the pat rules
        """
        interfaces : list[Interface] = self.get_interfaces_by_mac(mac)

        result = {}
        if ip_adresses:
            result["ip_addresses"] = self.__get_ip_addresses(interfaces)
        if passwords:
            result["passwords"] = self.__get_passwords(interfaces)
        if pat_rules:
            result["pat_rules"] = self.__get_pat_rules(interfaces)
        if main_unet_id:
            result["main_unet_id"] = self.__get_main_unet_id(interfaces)
        return result

if __name__ == "__main__":
    netbox = NetboxInterface2()
    # MAC address of boxes in netbox.dev.fai.rezel.net
    MAC_ADDRESS1 = "88:C3:97:14:B9:1F"
    MAC_ADDRESS2 = "88:C3:97:69:96:69"

    print(json.dumps(netbox.get_infos_by_mac(MAC_ADDRESS2), indent=4))
