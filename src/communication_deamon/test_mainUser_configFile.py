import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from communication_netbox.netbox import *
from MacAddress import MacAddress
from hermes_config_building.HermesConfigBuilder import *


MAC_ADDRESS2 = MacAddress("88:C3:97:69:96:69").getMac()
netbox = NetboxInterface()

json_data =netbox.get_raw_infos_by_mac(mac=MAC_ADDRESS2)
json_infos_by_mac=netbox.get_infos_by_mac(MAC_ADDRESS2)


#get usernetworkid and password from main user
passwords = json_infos_by_mac[1]
first_key = list(passwords.keys())[0]
print(passwords[first_key])



Netconf = UCINetworkConfig()
Fireconf = UCIFirewallConfig()
Dhcpconf = UCIDHCPConfig()
Wirelessconf = UCIWirelessConfig()
Dropbearconf = UCIDropbearConfig()

defconf = HermesAC2350DefaultConfig(UCI.DnsServers([UCI.IPAddress("8.8.8.8")]))

defconf.build_network(Netconf)
defconf.build_firewall(Fireconf)
defconf.build_dhcp(Dhcpconf)
defconf.build_wireless(Wirelessconf)
defconf.build_dropbear(Dropbearconf)

main_user = HermesMainUser(
    unetid=UCI.UNetId("main"),
    ssid=UCI.SSID("Rezel","MyWifi"),
    wan_address=UCI.IPAddress("137.194.8.2"),
    wan_netmask=UCI.IPAddress("255.255.255.0"),
    lan_address=UCI.IPAddress("192.168.0.1"),
    lan_network=UCI.IPNetwork("192.168.0.0/24"),
    wifi_passphrase=UCI.WifiPassphrase("password"),
    wan_vlan=101,
    default_config=defconf,
    default_router=UCI.IPAddress("137.194.8.1"))

main_user.build_network(Netconf)
main_user.build_firewall(Fireconf)
main_user.build_dhcp(Dhcpconf)
main_user.build_wireless(Wirelessconf)


# print(Netconf.build())
# print(Fireconf.build())
# print(Dhcpconf.build())
# print(Wirelessconf.build())





