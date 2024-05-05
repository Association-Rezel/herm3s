import json
from netaddr import IPNetwork
import re

from ...communication_netbox import NetboxInterface
from ..MacAddress import MacAddress
from ...hermes_command_building import common_command_builder as ccb
from ...hermes_command_building import ac2350
from ...hermes_command_building import uci_common as UCI
from ... import config


# function to create the configuration file of the main user
def create_configfile(mac_address: str):
    """create configuration file for all users
    Args:
        mac_address (str): mac address of the box
    return:
        void
    """
    Netconf = ccb.UCINetworkConfig()
    Fireconf = ccb.UCIFirewallConfig()
    Dhcpconf = ccb.UCIDHCPConfig()
    Wirelessconf = ccb.UCIWirelessConfig()
    Dropbearconf = ccb.UCIDropbearConfig()

    # create the default configuration
    defconf = ac2350.HermesDefaultConfig(UCI.DnsServers([UCI.IPAddress("8.8.8.8")]))

    defconf.build_network(Netconf)
    defconf.build_firewall(Fireconf)
    defconf.build_dhcp(Dhcpconf)
    defconf.build_wireless(Wirelessconf)
    defconf.build_dropbear(Dropbearconf)

    netbox = NetboxInterface()

    # get the infos by mac address
    json_infos_by_mac = netbox.get_infos_by_mac(mac_address)

    # get the main unet id
    unet_id_main_user = json_infos_by_mac["main_unet_id"]

    # count lan_vlan
    indice_lan_vlan = 1

    for key in json_infos_by_mac["ip_addresses"].keys():

        # check if  the unet_id has the good form
        if re.match(r"^[a-z0-9]{8}$", key) is None:
            raise ValueError("Invalid UNetId")

        indice = 0
        # config file main user
        if key == unet_id_main_user:
            for i in range(len(json_infos_by_mac["ip_addresses"][key])):
                if json_infos_by_mac["ip_addresses"][key][i]["name"] != "eth0.65":
                    # indice of the good interface (not eth0.65)
                    indice = i

            # get passord of the main user
            password_main_user = json_infos_by_mac["passwords"][key]

            # get SSID from the unet id
            SSID = json_infos_by_mac["ssids"][key]

            # get wan ip address of the main user
            wan_ip_address = json_infos_by_mac["ip_addresses"][key][indice][
                "ip_address"
            ][:-3]

            # calculate the netmask with netaddr
            wan_ip_netmask = str(
                IPNetwork(
                    json_infos_by_mac["ip_addresses"][key][indice]["ip_address"]
                ).netmask
            )

            # get lan ip address of the main user
            lan_ip_address = json_infos_by_mac["ip_addresses"][key][indice][
                "nat_inside_ip"
            ][:-3]

            # calculate the network with netaddr
            lan_ip_network = str(
                IPNetwork(
                    json_infos_by_mac["ip_addresses"][key][indice]["nat_inside_ip"]
                ).cidr
            )

            # get wan_wlan number of the main user
            wan_vlan_number = int(
                json_infos_by_mac["ip_addresses"][key][indice]["name"].split("eth0.")[1]
            )

            # get the default router ip address
            default_router_ip_address = config.DEF_ROUTER_IP_VLAN[
                wan_vlan_number
            ]

            # create the main user configuration
            main_user = ac2350.HermesMainUser(
                unetid=UCI.UNetId(key),
                ssid=UCI.SSID(SSID),
                wan_address=UCI.IPAddress(wan_ip_address),
                wan_netmask=UCI.IPAddress(wan_ip_netmask),
                lan_address=UCI.IPAddress(lan_ip_address),
                lan_network=UCI.IPNetwork(lan_ip_network),
                wifi_passphrase=UCI.WifiPassphrase(password_main_user),
                wan_vlan=wan_vlan_number,
                lan_vlan=indice_lan_vlan,
                default_config=defconf,
                default_router=UCI.IPAddress(default_router_ip_address),
            )
            main_user.build_network(Netconf)
            main_user.build_firewall(Fireconf)
            main_user.build_dhcp(Dhcpconf)
            main_user.build_wireless(Wirelessconf)

            # create port forwarding for the main user
            for dico in json_infos_by_mac["pat_rules"]:
                if dico["unet_id"] == key:

                    # get source port
                    outside_port = dico["outside_port"]

                    # get dest port and ip
                    inside_port = dico["inside_port"]
                    inside_ip = dico["inside_ip"][:-3]

                    protocol = dico["protocol"]

                    main_port_forwarding = ac2350.HermesPortForwarding(
                        unetid=UCI.UNetId(key),
                        name=UCI.UCISectionName("http_to_internal"),
                        desc=UCI.Description("HTTP forwarding"),
                        src=main_user.wan_zone,
                        src_dport=UCI.TCPUDPPort(outside_port),
                        dest=main_user.lan_zone,
                        dest_ip=UCI.IPAddress(inside_ip),
                        dest_port=UCI.TCPUDPPort(inside_port),
                        proto=UCI.Protocol(protocol),
                    )
                    main_port_forwarding.build_firewall(Fireconf)

        else:
            # get passord of the main user
            password_other_user = json_infos_by_mac["passwords"][key]

            # get SSID from the unet id
            SSID = json_infos_by_mac["ssids"][key]

            # get wan ip address of the main user
            wan_ip_address = json_infos_by_mac["ip_addresses"][key][indice][
                "ip_address"
            ][:-3]

            # calculate the netmask with netaddr
            wan_ip_netmask = str(
                IPNetwork(
                    json_infos_by_mac["ip_addresses"][key][indice]["ip_address"]
                ).netmask
            )

            # get lan ip address of the main user
            lan_ip_address = json_infos_by_mac["ip_addresses"][key][indice][
                "nat_inside_ip"
            ][:-3]

            # calculate the network with netaddr
            lan_ip_network = str(
                IPNetwork(
                    json_infos_by_mac["ip_addresses"][key][indice]["nat_inside_ip"]
                ).cidr
            )

            # get wan_wlan number of the main user
            wan_vlan_number = int(
                json_infos_by_mac["ip_addresses"][key][indice]["name"].split("eth0.")[1]
            )

            # cf si IP de dodo/ptero et si c le même selon si c un télécommien ou non (faire condition sur vlan sinon)
            default_router_ip_address = config.DEF_ROUTER_IP_VLAN[
                wan_vlan_number
            ]

            # create the other user configuration
            other_user = ac2350.HermesSecondaryUser(
                unetid=UCI.UNetId(key),
                ssid=UCI.SSID(SSID),
                wan_address=UCI.IPAddress(wan_ip_address),
                wan_netmask=UCI.IPAddress(wan_ip_netmask),
                lan_address=UCI.IPAddress(lan_ip_address),
                lan_network=UCI.IPNetwork(lan_ip_network),
                lan_vlan=indice_lan_vlan,
                wifi_passphrase=UCI.WifiPassphrase(password_other_user),
                wan_vlan=wan_vlan_number,
                default_config=defconf,
                default_router=UCI.IPAddress(default_router_ip_address),
            )
            other_user.build_network(Netconf)
            other_user.build_firewall(Fireconf)
            other_user.build_dhcp(Dhcpconf)
            other_user.build_wireless(Wirelessconf)

            # create port forwarding for the other user
            for dico in json_infos_by_mac["pat_rules"]:
                if dico["unet_id"] == key:

                    # get source port
                    outside_port = dico["outside_port"]

                    # get dest port and ip
                    inside_port = dico["inside_port"]
                    inside_ip = dico["inside_ip"][:-3]

                    protocol = dico["protocol"]

                    main_port_forwarding = ac2350.HermesPortForwarding(
                        unetid=UCI.UNetId(key),
                        name=UCI.UCISectionName("http_to_internal"),
                        desc=UCI.Description("HTTP forwarding"),
                        src=main_user.wan_zone,
                        src_dport=UCI.TCPUDPPort(outside_port),
                        dest=main_user.lan_zone,
                        dest_ip=UCI.IPAddress(inside_ip),
                        dest_port=UCI.TCPUDPPort(inside_port),
                        proto=UCI.Protocol(protocol),
                    )
                    main_port_forwarding.build_firewall(Fireconf)

        # update lan_vlan
        indice_lan_vlan += 1

    # add to the configfile
    with open(
        f"{config.FILE_SAVING_PATH}configfile_" + mac_address + ".txt", "w"
    ) as file:
        file.write(
            Netconf.build()
            + "/--SEPARATOR--/\n"
            + Fireconf.build()
            + "/--SEPARATOR--/\n"
            + Dhcpconf.build()
            + "/--SEPARATOR--/\n"
            + Wirelessconf.build()
            + "/--SEPARATOR--/\n"
            + Dropbearconf.build()
        )


def create_default_configfile():
    """create configuration file for all users
     Args:
        void
    return:
        void
    """
    Netconf = ccb.UCINetworkConfig()
    Fireconf = ccb.UCIFirewallConfig()
    Dhcpconf = ccb.UCIDHCPConfig()
    Wirelessconf = ccb.UCIWirelessConfig()
    Dropbearconf = ccb.UCIDropbearConfig()

    # create the default configuration
    defconf = ac2350.HermesDefaultConfig(UCI.DnsServers([UCI.IPAddress("8.8.8.8")]))

    defconf.build_network(Netconf)
    defconf.build_firewall(Fireconf)
    defconf.build_dhcp(Dhcpconf)
    defconf.build_wireless(Wirelessconf)
    defconf.build_dropbear(Dropbearconf)

    with open(f"{config.FILE_SAVING_PATH}defaultConfigfile.txt", "w") as file:
        file.write(
            Netconf.build()
            + "/--SEPARATOR--/\n"
            + Fireconf.build()
            + "/--SEPARATOR--/\n"
            + Dhcpconf.build()
            + "/--SEPARATOR--/\n"
            + Wirelessconf.build()
            + "/--SEPARATOR--/\n"
            + Dropbearconf.build()
        )


if __name__ == "__main__":
    mac_address = MacAddress("88:C3:97:69:96:69").getMac()
    netbox = NetboxInterface()

    # # get the infos by mac address
    json_infos_by_mac = netbox.get_infos_by_mac(mac_address)
    create_configfile(mac_address)
    create_default_configfile()
    print(json.dumps(json_infos_by_mac, indent=4))
    print(
        IPNetwork(
            json_infos_by_mac["ip_addresses"]["unet_id_666_1"][0]["nat_inside_ip"]
        ).cidr
    )
    print(
        str(
            IPNetwork(
                json_infos_by_mac["ip_addresses"]["unet_id_666_0"][1]["ip_address"]
            ).netmask
        )
    )
