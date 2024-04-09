import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from communication_netbox.netbox import *
from MacAddress import MacAddress
from hermes_config_building.HermesConfigBuilder import *



MAC_ADDRESS2 = MacAddress("88:C3:97:69:96:69").getMac()
netbox = NetboxInterface()

# # get the infos by mac address
json_infos_by_mac=netbox.get_infos_by_mac(MAC_ADDRESS2)
print(json.dumps(json_infos_by_mac,indent=4))
print(int(json_infos_by_mac["ip_addresses"]["unet_id_666_0"][1]["name"].split("eth0.")[1]))



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
def create_configfile(MAC_ADDRESS:str):
    """create configuration file for all users
    Args:
        MAC_ADDRESS (str): mac address of the box
    return:
        void
        """
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



    netbox = NetboxInterface()
    # get the infos by mac address
    json_infos_by_mac=netbox.get_infos_by_mac(MAC_ADDRESS2)

    # get the main unet id 
    unet_id_main_user = json_infos_by_mac["main_unet_id"]

    for key in json_infos_by_mac["ip_addresses"].keys():

        #config file main user
        if key==unet_id_main_user:
            #get passord of the main user
            password_main_user = json_infos_by_mac["passwords"][unet_id_main_user]

            # get SSID from the unet id
            SSID = unet_id_main_user.split("unet")[1]
            
            # get wan ip address of the main user
            wan_ip_address = json_infos_by_mac["ip_addresses"][key][1]["ip_address"][:-3]
            wan_ip_netmask = "255.255.255.0"  #always the same ???

            # get lan ip address of the main user
            lan_ip_address = json_infos_by_mac["ip_addresses"][key][1]["nat_inside_ip"][:-3]
            lan_ip_network = "192.168.0.0/24"   #always the same ???

            # get wan_wlan number of the main user
            wan_vlan_number = int(json_infos_by_mac["ip_addresses"][key][1]["name"].split("eth0.")[1])

            # cf si IP de dodo/ptero et si c le même selon si c un télécommien ou non
            default_router_ip_address = "137.194.11.254"

            # create the main user configuration
            main_user = HermesMainUser(
            unetid=UCI.UNetId(unet_id_main_user),
            ssid=UCI.SSID("Rezel",SSID),
            wan_address=UCI.IPAddress(wan_ip_address),
            wan_netmask=UCI.IPAddress(wan_ip_netmask),
            lan_address=UCI.IPAddress(lan_ip_address),
            lan_network=UCI.IPNetwork(lan_ip_network),
            wifi_passphrase=UCI.WifiPassphrase(password_main_user),
            wan_vlan=wan_vlan_number,
            default_config=defconf, #utility ???
            default_router=UCI.IPAddress(default_router_ip_address))

            main_user.build_network(Netconf)
            main_user.build_firewall(Fireconf)
            main_user.build_dhcp(Dhcpconf)
            main_user.build_wireless(Wirelessconf)
        
        else:
            #get passord of the main user
            password_other_user = json_infos_by_mac["passwords"][key]

            # get SSID from the unet id
            SSID = key.split("unet")[1]
            
            # get wan ip address of the main user
            wan_ip_address = json_infos_by_mac["ip_addresses"][key][0]["ip_address"][:-3]
            wan_ip_netmask = "255.255.255.0"  #always the same ???

            # get lan ip address of the main user
            lan_ip_address = json_infos_by_mac["ip_addresses"][key][0]["nat_inside_ip"][:-3]
            lan_ip_network = "192.168.0.0/24"   #always the same ???

            # get wan_wlan number of the main user
            wan_vlan_number = int(json_infos_by_mac["ip_addresses"][key][0]["name"].split("eth0.")[1])

            # cf si IP de dodo/ptero et si c le même selon si c un télécommien ou non (faire condition sur vlan sinon)
            default_router_ip_address = "137.194.11.254"

            # create the other user configuration
            other_user = HermesSecondaryUser(
            unetid=UCI.UNetId(key),
            ssid=UCI.SSID("Rezel",SSID),
            wan_address=UCI.IPAddress(wan_ip_address),
            wan_netmask=UCI.IPAddress(wan_ip_netmask),
            lan_address=UCI.IPAddress(lan_ip_address),
            lan_network=UCI.IPNetwork(lan_ip_network),
            wifi_passphrase=UCI.WifiPassphrase(password_other_user),
            wan_vlan=wan_vlan_number,
            default_config=defconf,
            default_router=UCI.IPAddress(default_router_ip_address)
            )
            other_user.build_network(Netconf)
            other_user.build_firewall(Fireconf)
            other_user.build_dhcp(Dhcpconf)
            other_user.build_wireless(Wirelessconf)
            

    #add to the config_file
    with open ("configfile.txt","w") as file:
        file.write(Netconf.build()+Fireconf.build()+Dhcpconf.build()+Wirelessconf.build()+Dropbearconf.build())
        
    
    


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





