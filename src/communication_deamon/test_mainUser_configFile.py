import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from communication_netbox.netbox import *
from MacAddress import MacAddress
from hermes_config_building.HermesConfigBuilder import *



MAC_ADDRESS2 = MacAddress("88:C3:97:69:96:69").getMac()
# netbox = NetboxInterface2()

# # get the infos by mac address
# json_infos_by_mac=netbox.get_infos_by_mac(MAC_ADDRESS2)
# print(json.dumps(json_infos_by_mac,indent=4))


# # get the main unet id with his password
# unet_id_main_user = json_infos_by_mac["main_unet_id"]
# password_main_user = json_infos_by_mac["passwords"][unet_id_main_user]
# print(unet_id_main_user)
# print(password_main_user)

# # get SSID from the unet id
# SSID = unet_id_main_user.split("unet")[1]
# print(SSID) 

# # get wan ip address of the main user
# test = netbox.get_interfaces_by_mac(MAC_ADDRESS2)
# print(test["ip_addresses"])



# function to create the configuration file of the main user
def create_main_user_config_file(MAC_ADDRESS:str):
    """Create the configuration file of the main user
    Args:
        MAC_ADDRESS (str) : the mac address of the main user

    Returns: 
        config_file (dict) : the configuration file of the main user"""

    config_file = {}

    netbox = NetboxInterface2()

    # get the infos by mac address
    json_infos_by_mac=netbox.get_infos_by_mac(MAC_ADDRESS2)

    # get the main unet id with his password
    unet_id_main_user = json_infos_by_mac["main_unet_id"]
    password_main_user = json_infos_by_mac["passwords"][unet_id_main_user]

    # get SSID from the unet id
    SSID = unet_id_main_user.split("unet")[1]

    #TODO : get the wan ip address
    # get wan ip address of the main user
    wan_ip_address = "137.194.8.2"
    wan_ip_netmask = "255.255.255.0"

    #TODO : get the lan ip address
    # get lan ip address of the main user
    lan_ip_address = "192.168.2.0"
    lan_ip_network = "192.168.0.0/24"

    #TODO : get wan_wlan of the main user
    # get wan vlan of the main user
    wan_vlan_number = 101

    #TODO : get the default router
    # cf si IP de dodo/ptero et si c le même selon si c un télécommien ou non
    default_router_ip_address = "137.194.11.254"

    
    Netconf = UCINetworkConfig()
    Fireconf = UCIFirewallConfig()
    Dhcpconf = UCIDHCPConfig()
    Wirelessconf = UCIWirelessConfig()
    Dropbearconf = UCIDropbearConfig()

    # create the default configuration
    defconf = HermesAC2350DefaultConfig(UCI.DnsServers([UCI.IPAddress("8.8.8.8")]))

    defconf.build_network(Netconf)
    defconf.build_firewall(Fireconf)
    defconf.build_dhcp(Dhcpconf)
    defconf.build_wireless(Wirelessconf)
    defconf.build_dropbear(Dropbearconf)

    # create the main user configuration

    main_user = HermesMainUser(
    unetid=UCI.UNetId(unet_id_main_user),
    ssid=UCI.SSID("Rezel",SSID),
    wan_address=UCI.IPAddress(wan_ip_address),
    wan_netmask=UCI.IPAddress(wan_ip_netmask),
    lan_address=UCI.IPAddress(lan_ip_address),
    lan_network=UCI.IPNetwork(lan_ip_network),
    wifi_passphrase=UCI.WifiPassphrase(password_main_user),
    wan_vlan=101,
    default_config=defconf,
    default_router=UCI.IPAddress(default_router_ip_address))

    main_user.build_network(Netconf)
    config_file["network"] = Netconf.build()

    main_user.build_firewall(Fireconf)
    config_file["firewall"] = Fireconf.build()

    main_user.build_dhcp(Dhcpconf)
    config_file["dhcp"] = Dhcpconf.build()

    main_user.build_wireless(Wirelessconf)
    config_file["wireless"] = Wirelessconf.build()

    config_file["dropbear"] = Dropbearconf.build()

    return config_file
    
# print(json.dumps(create_main_user_config_file(MAC_ADDRESS2),indent = 4))

# Netconf = UCINetworkConfig()
# Fireconf = UCIFirewallConfig()
# Dhcpconf = UCIDHCPConfig()
# Wirelessconf = UCIWirelessConfig()
# Dropbearconf = UCIDropbearConfig()

# defconf = HermesAC2350DefaultConfig(UCI.DnsServers([UCI.IPAddress("8.8.8.8")]))

# defconf.build_network(Netconf)
# defconf.build_firewall(Fireconf)
# defconf.build_dhcp(Dhcpconf)
# defconf.build_wireless(Wirelessconf)
# defconf.build_dropbear(Dropbearconf)

# main_user = HermesMainUser(
#     unetid=UCI.UNetId("main"),
#     ssid=UCI.SSID("Rezel","MyWifi"),
#     wan_address=UCI.IPAddress("137.194.8.2"),
#     wan_netmask=UCI.IPAddress("255.255.255.0"),
#     lan_address=UCI.IPAddress("192.168.0.1"),
#     lan_network=UCI.IPNetwork("192.168.0.0/24"),
#     wifi_passphrase=UCI.WifiPassphrase("password"),
#     wan_vlan=101,
#     default_config=defconf,
#     default_router=UCI.IPAddress("137.194.8.1"))

# main_user.build_network(Netconf)
# main_user.build_firewall(Fireconf)
# main_user.build_dhcp(Dhcpconf)
# main_user.build_wireless(Wirelessconf)


# print(Netconf.build())
# print(Fireconf.build())
# print(Dhcpconf.build())
# print(Wirelessconf.build())





