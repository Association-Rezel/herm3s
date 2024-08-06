from netaddr import EUI, IPNetwork, mac_unix_expanded

from hermes.env import ENV
from hermes.hermes_command_building import ac2350
from hermes.hermes_command_building import common_command_builder as ccb
from hermes.hermes_command_building import uci_common as UCI
from hermes.mongodb.models import Box


def create_configfile(box: Box):
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
    defconf = ac2350.HermesDefaultConfig()

    defconf.build_network(Netconf)
    defconf.build_firewall(Fireconf)
    defconf.build_dhcp(Dhcpconf)
    defconf.build_wireless(Wirelessconf)
    defconf.build_dropbear(Dropbearconf)

    # Get the main unet id
    main_user_unetid = box.main_unet_id

    for unet in box.unets:

        wan_ip_address = IPNetwork(unet.network.wan_ipv4.ip).ip
        wan_ip_netmask = str(IPNetwork(unet.network.wan_ipv4.ip).netmask)
        lan_ip_address = IPNetwork(unet.network.lan_ipv4.address).ip
        lan_ip_network = str(IPNetwork(unet.network.lan_ipv4.address).cidr)

        try:
            default_router_v4 = IPNetwork(
                next(
                    # The weird lambda is to avoid a closure issue
                    filter(
                        lambda vlan, unet_vlan=unet.network.wan_ipv4.vlan: vlan.vlan_id
                        == unet_vlan,
                        box.wan_vlan,
                    ),
                    None,
                ).ipv4_gateway
            ).ip
        except StopIteration:
            print(f"Error: No matching VLAN found for {unet.network.wan_ipv4.vlan}")
        try:
            default_router_v6 = IPNetwork(
                next(
                    filter(
                        lambda vlan, unet_vlan=unet.network.wan_ipv6.vlan: vlan.vlan_id
                        == unet_vlan,
                        box.wan_vlan,
                    ),
                    None,
                ).ipv6_gateway
            ).ip
        except StopIteration:
            print(f"Error: No matching VLAN found for {unet.network.wan_ipv6.vlan}")

        if unet.unet_id == main_user_unetid:
            user = ac2350.HermesMainUser(
                unetid=UCI.UNetId(unet.unet_id),
                ssid=UCI.SSID(unet.wifi.ssid),
                wan_address=UCI.IPAddress(wan_ip_address),
                wan_netmask=UCI.IPAddress(wan_ip_netmask),
                lan_address=UCI.IPAddress(lan_ip_address),
                lan_network=UCI.IPNetwork(lan_ip_network),
                wifi_passphrase=UCI.WifiPassphrase(unet.wifi.psk),
                dns_servers_v4=UCI.DnsServers(
                    [UCI.IPAddress(dns) for dns in unet.dhcp.dns_servers.ipv4]
                ),
                dns_servers_v6=UCI.DnsServers(
                    [UCI.IPAddress(dns) for dns in unet.dhcp.dns_servers.ipv6]
                ),
                wan_vlan=unet.network.wan_ipv4.vlan,
                lan_vlan=unet.network.lan_ipv4.vlan,
                default_config=defconf,
                default_router=UCI.IPAddress(default_router_v4),
                wan6_address=UCI.IPNetwork(unet.network.wan_ipv6.ip),
                unet6_prefix=UCI.IPNetwork(unet.network.ipv6_prefix),
                wan6_vlan=unet.network.wan_ipv6.vlan,
                default_router6=UCI.IPAddress(default_router_v6),
            )
        else:
            user = ac2350.HermesSecondaryUser(
                unetid=UCI.UNetId(unet.unet_id),
                ssid=UCI.SSID(unet.wifi.ssid),
                wan_address=UCI.IPAddress(wan_ip_address),
                wan_netmask=UCI.IPAddress(wan_ip_netmask),
                lan_address=UCI.IPAddress(lan_ip_address),
                lan_network=UCI.IPNetwork(lan_ip_network),
                lan_vlan=unet.network.lan_ipv4.vlan,
                wifi_passphrase=UCI.WifiPassphrase(unet.wifi.psk),
                dns_servers_v4=UCI.DnsServers(
                    [UCI.IPAddress(dns) for dns in unet.dhcp.dns_servers.ipv4]
                ),
                dns_servers_v6=UCI.DnsServers(
                    [UCI.IPAddress(dns) for dns in unet.dhcp.dns_servers.ipv6]
                ),
                wan_vlan=unet.network.wan_ipv4.vlan,
                default_config=defconf,
                default_router=UCI.IPAddress(default_router_v4),
                wan6_address=UCI.IPNetwork(unet.network.wan_ipv6.ip),
                unet6_prefix=UCI.IPNetwork(unet.network.ipv6_prefix),
                wan6_vlan=unet.network.wan_ipv6.vlan,
                default_router6=UCI.IPAddress(default_router_v6),
            )

        user.build_network(Netconf)
        user.build_firewall(Fireconf)
        user.build_dhcp(Dhcpconf)
        user.build_wireless(Wirelessconf)

        # Create port forwarding
        for port_forwarding in unet.firewall.ipv4_port_forwarding:
            user_port_forwarding = ac2350.HermesPortForwarding(
                unetid=UCI.UNetId(unet.unet_id),
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

    # Add to the config file
    with open(
        f"{ENV.temp_generated_box_configs_dir}configfile_" + str(box.mac) + ".txt",
        "w",
        encoding="utf-8",
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
    defconf = ac2350.HermesDefaultConfig()

    defconf.build_network(Netconf)
    defconf.build_firewall(Fireconf)
    defconf.build_dhcp(Dhcpconf)
    defconf.build_wireless(Wirelessconf)
    defconf.build_dropbear(Dropbearconf)

    with open(
        f"{ENV.temp_generated_box_configs_dir}defaultConfigfile.txt",
        "w",
        encoding="utf_8",
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


if __name__ == "__main__":
    mac = EUI("00:00:00:00:00:00")
    mac.dialect = mac_unix_expanded
    create_configfile(mac)
