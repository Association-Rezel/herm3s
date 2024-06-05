import json
from netaddr import IPNetwork
import re

from ...communication_db.db_api import DbApi
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

    db_api = DbApi()

    # get the infos by mac address
    box = db_api.get_box_by_mac(mac_address)

    # get the main unet id
    unet_id_main_user = box.main_unet_id

    # count lan_vlan
    indice_lan_vlan = 1

    for unet_profile in box.unets:

        # configure file main user
        if unet_profile.unet_id == unet_id_main_user:
            password_main_user = unet_profile.wifi.psk
            SSID = unet_profile.wifi.ssid

            # get wan ip address of the main user
            wan_ip_address = IPNetwork(unet_profile.network.wan_ipv4.ip).ip

            # calculate the netmask with netaddr
            wan_ip_netmask = str(IPNetwork(unet_profile.network.wan_ipv4.ip).netmask)

            # get lan ip address of the main user
            lan_ip_address = IPNetwork(unet_profile.network.lan_ipv4.net).ip

            # calculate the network with netaddr
            lan_ip_network = str(IPNetwork(unet_profile.network.lan_ipv4.net).cidr)

            # get wan_vlan number of the main user
            wan_vlan_number = int(unet_profile.network.wan_ipv4.vlan)

            # get the default router ip address
            default_router_ip_address = config.DEF_ROUTER_IP_VLAN[str(wan_vlan_number)]

            # create the main user configuration
            main_user = ac2350.HermesMainUser(
                unetid=UCI.UNetId(unet_profile.unet_id),
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
            for port_forwarding in unet_profile.firewall.ipv4_port_forwarding:
                main_port_forwarding = ac2350.HermesPortForwarding(
                    unetid=UCI.UNetId(unet_profile.unet_id),
                    name=UCI.UCISectionName("http_to_internal"),
                    desc=UCI.Description("HTTP forwarding"),
                    src=main_user.wan_zone,
                    src_dport=UCI.TCPUDPPort(port_forwarding.wan_port),
                    dest=main_user.lan_zone,
                    dest_ip=UCI.IPAddress(port_forwarding.lan_ip),
                    dest_port=UCI.TCPUDPPort(port_forwarding.lan_port),
                    proto=UCI.Protocol(port_forwarding.protocol),
                )
                main_port_forwarding.build_firewall(Fireconf)

        else:
            password_other_user = unet_profile.wifi.psk
            SSID = unet_profile.wifi.ssid

            # get wan ip address of the other user
            wan_ip_address = IPNetwork(unet_profile.network.wan_ipv4.ip).ip

            # calculate the netmask with netaddr
            wan_ip_netmask = str(IPNetwork(unet_profile.network.wan_ipv4.ip).netmask)

            # get lan ip address of the main user
            lan_ip_address = IPNetwork(unet_profile.network.lan_ipv4.net).ip

            # calculate the network with netaddr
            lan_ip_network = str(IPNetwork(unet_profile.network.lan_ipv4.net).cidr)

            # get wan_vlan number of the other user
            wan_vlan_number = int(unet_profile.network.wan_ipv4.vlan)

            # cf si IP de dodo/ptero et si c le même selon si c un télécommien ou non (faire condition sur vlan sinon)
            default_router_ip_address = config.DEF_ROUTER_IP_VLAN[str(wan_vlan_number)]

            # create the other user configuration
            other_user = ac2350.HermesSecondaryUser(
                unetid=UCI.UNetId(unet_profile.unet_id),
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
            for port_forwarding in unet_profile.firewall.ipv4_port_forwarding:
                main_port_forwarding = ac2350.HermesPortForwarding(
                    unetid=UCI.UNetId(unet_profile.unet_id),
                    name=UCI.UCISectionName("http_to_internal"),
                    desc=UCI.Description("HTTP forwarding"),
                    src=main_user.wan_zone,
                    src_dport=UCI.TCPUDPPort(port_forwarding.wan_port),
                    dest=main_user.lan_zone,
                    dest_ip=UCI.IPAddress(port_forwarding.lan_ip),
                    dest_port=UCI.TCPUDPPort(port_forwarding.lan_port),
                    proto=UCI.Protocol(port_forwarding.protocol),
                )
                main_port_forwarding.build_firewall(Fireconf)

        # update lan_vlan
        indice_lan_vlan += 1

    # add to the configfile
    with open(
        f"{config.FILE_SAVING_PATH}configfile_" + mac_address + ".txt", "w"
    ) as file:
        file.write(
            "/-- SEPARATOR network --/\n"
            + Netconf.build()
            + "/-- SEPARATOR firewall --/\n"
            + Fireconf.build()
            + "/-- SEPARATOR dhcp --/\n"
            + Dhcpconf.build()
            + "/-- SEPARATOR wireless --/\n"
            + Wirelessconf.build()
            + "/-- SEPARATOR dropbear --/\n"
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
            "/-- SEPARATOR network --/\n"
            + Netconf.build()
            + "/-- SEPARATOR firewall --/\n"
            + Fireconf.build()
            + "/-- SEPARATOR dhcp --/\n"
            + Dhcpconf.build()
            + "/-- SEPARATOR wireless --/\n"
            + Wirelessconf.build()
            + "/-- SEPARATOR dropbear --/\n"
            + Dropbearconf.build()
        )


if __name__ == "__main__":
    mac_address = MacAddress("00:00:00:00:00:00").getMac()
    create_configfile(mac_address)
