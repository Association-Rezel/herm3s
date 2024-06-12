from netaddr import IPNetwork

from ...communication_db.db_api import DbApi
from ..MacAddress import MacAddress
from ...hermes_command_building import common_command_builder as ccb
from ...hermes_command_building import ac2350
from ...hermes_command_building import uci_common as UCI
from ... import config


def create_configfile(mac_address: str):
    """
    Function to create the configuration files for all users

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

    # Create the default configuration
    defconf = ac2350.HermesDefaultConfig(UCI.DnsServers([UCI.IPAddress("8.8.8.8")]))

    defconf.build_network(Netconf)
    defconf.build_firewall(Fireconf)
    defconf.build_dhcp(Dhcpconf)
    defconf.build_wireless(Wirelessconf)
    defconf.build_dropbear(Dropbearconf)

    db_api = DbApi()

    # Get the infos by mac address
    box = db_api.get_box_by_mac(mac_address)

    # Get the main unet id
    unet_id_main_user = box.main_unet_id

    # Count lan_vlan
    indice_lan_vlan = 1

    for unet_profile in box.unets:

        wan_ip_address = IPNetwork(unet_profile.network.wan_ipv4.ip).ip
        wan_ip_netmask = str(IPNetwork(unet_profile.network.wan_ipv4.ip).netmask)
        lan_ip_address = IPNetwork(unet_profile.network.lan_ipv4.net).ip
        lan_ip_network = str(IPNetwork(unet_profile.network.lan_ipv4.net).cidr)
        wan_vlan_number = int(unet_profile.network.wan_ipv4.vlan)
        default_router_ip_address = config.DEF_ROUTER_IP_VLAN[str(wan_vlan_number)]

        default_router_v6 = (
            next(
                vlan
                for vlan in box.wan_vlan
                if vlan.vlan_id == unet_profile.network.wan_ipv6.vlan
            )
            .net_gateway[0]
            .gateway.ip
        )

        if unet_profile.unet_id == unet_id_main_user:
            user = ac2350.HermesMainUser(
                unetid=UCI.UNetId(unet_profile.unet_id),
                ssid=UCI.SSID(unet_profile.wifi.ssid),
                wan_address=UCI.IPAddress(wan_ip_address),
                wan_netmask=UCI.IPAddress(wan_ip_netmask),
                lan_address=UCI.IPAddress(lan_ip_address),
                lan_network=UCI.IPNetwork(lan_ip_network),
                wifi_passphrase=UCI.WifiPassphrase(unet_profile.wifi.psk),
                wan_vlan=wan_vlan_number,
                lan_vlan=indice_lan_vlan,
                default_config=defconf,
                default_router=UCI.IPAddress(default_router_ip_address),
                wan6_address=UCI.IPNetwork(
                    str(IPNetwork(unet_profile.network.wan_ipv6.ip).ip)
                ),
                unet6_prefix=IPNetwork(
                    str(IPNetwork(unet_profile.network.ipv6_prefix).ip)
                ),
                wan6_vlan=int(unet_profile.network.wan_ipv6.vlan),
                default_router6=UCI.IPAddress(default_router_v6),
            )
        else:
            user = ac2350.HermesSecondaryUser(
                unetid=UCI.UNetId(unet_profile.unet_id),
                ssid=UCI.SSID(unet_profile.wifi.ssid),
                wan_address=UCI.IPAddress(wan_ip_address),
                wan_netmask=UCI.IPAddress(wan_ip_netmask),
                lan_address=UCI.IPAddress(lan_ip_address),
                lan_network=UCI.IPNetwork(lan_ip_network),
                lan_vlan=indice_lan_vlan,
                wifi_passphrase=UCI.WifiPassphrase(unet_profile.wifi.psk),
                wan_vlan=wan_vlan_number,
                default_config=defconf,
                default_router=UCI.IPAddress(default_router_ip_address),
                wan6_address=UCI.IPNetwork(
                    str(IPNetwork(unet_profile.network.wan_ipv6.ip).ip)
                ),
                unet6_prefix=IPNetwork(
                    str(IPNetwork(unet_profile.network.ipv6_prefix).ip)
                ),
                wan6_vlan=int(unet_profile.network.wan_ipv6.vlan),
                default_router6=UCI.IPAddress(default_router_v6),
            )

        user.build_network(Netconf)
        user.build_firewall(Fireconf)
        user.build_dhcp(Dhcpconf)
        user.build_wireless(Wirelessconf)

        # Create port forwarding
        for port_forwarding in unet_profile.firewall.ipv4_port_forwarding:
            user_port_forwarding = ac2350.HermesPortForwarding(
                unetid=UCI.UNetId(unet_profile.unet_id),
                name=UCI.UCISectionName("http_to_internal"),
                desc=UCI.Description("HTTP forwarding"),
                src=user.wan_zone,
                src_dport=UCI.TCPUDPPort(port_forwarding.wan_port),
                dest=user.lan_zone,
                dest_ip=UCI.IPAddress(port_forwarding.lan_ip),
                dest_port=UCI.TCPUDPPort(port_forwarding.lan_port),
                proto=UCI.Protocol(port_forwarding.protocol),
            )
            user_port_forwarding.build_firewall(Fireconf)

        # Update lan_vlan
        indice_lan_vlan += 1

    # Add to the config file
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
    """
    Function to create the default configuration files for all users

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
