from .uci_common import uci_common as UCI
from . import common_command_builder as ccb


class HermesDefaultConfig(ccb.HermesDefaultConfig):
    """
    Represents the default configuration for the Hermes AC2350 router.
    Herits from HermesDefaultConfig
    """

    loopback: UCI.UCIInterface
    switch0: UCI.UCISwitch
    vlan_1: UCI.UCISwitchVlan
    vlan_65: UCI.UCISwitchVlan
    vlan_101: UCI.UCISwitchVlan
    vlan_102: UCI.UCISwitchVlan
    vlan_103: UCI.UCISwitchVlan
    management: UCI.UCINoIPInterface
    radio0: UCI.UCIWifiDevice
    radio1: UCI.UCIWifiDevice

    def __init__(self, dns_servers: UCI.DnsServers):
        super().__init__()
        # Network Configuration
        self.loopback = UCI.UCIInterface(
            UCI.UCISectionNamePrefix("loopback"),
            UCI.IPAddress("127.0.0.1"),
            UCI.IPAddress("255.0.0.0"),
            UCI.InterfaceProto("static"),
            device=UCI.UCISimpleDevice("lo"),
        )
        self.network_commands.append(self.loopback)
        self.network_commands.append(UCI.UCINetGlobals("fdb2:b6c0:8430::/48"))
        self.switch0 = UCI.UCISwitch("switch0")
        self.network_commands.append(self.switch0)
        self.vlan_65 = UCI.UCISwitchVlan(
            UCI.UCISectionName("vlan_65"),
            self.switch0,
            65,
            UCI.UCINetworkPorts("1t 0t"),
        )
        self.network_commands.append(self.vlan_65)
        self.management = UCI.UCINoIPInterface(
            UCI.UCISectionName("management"), UCI.UCISimpleDevice("eth0.65")
        )
        self.network_commands.append(self.management)
        self.vlan_101 = UCI.UCISwitchVlan(
            name=UCI.UCISectionName("vlan_101"),
            device=self.switch0,
            vid=101,
            ports=UCI.UCINetworkPorts("1t 0t"),
        )
        self.network_commands.append(self.vlan_101)
        self.vlan_102 = UCI.UCISwitchVlan(
            name=UCI.UCISectionName("vlan_102"),
            device=self.switch0,
            vid=102,
            ports=UCI.UCINetworkPorts("1t 0t"),
        )
        self.network_commands.append(self.vlan_102)
        self.vlan_103 = UCI.UCISwitchVlan(
            name=UCI.UCISectionName("vlan_103"),
            device=self.switch0,
            vid=103,
            ports=UCI.UCINetworkPorts("1t 0t"),
        )
        self.network_commands.append(self.vlan_103)

        # Firewall Configuration
        self.firewall_commands.append(UCI.UCIFirewallDefaults())

        # DHCP Configuration
        self.dhcp_commands.append(UCI.UCIdnsmasq(dns_servers))
        self.dhcp_commands.append(UCI.UCIodchp())

        # Wireless Configuration
        self.radio0 = UCI.UCIWifiDevice(
            name=UCI.UCISectionName("radio0"),
            path=UCI.Path("pci0000:00/0000:00:00.0"),
            device_type=UCI.WifiDeviceType("mac80211"),
            channel=UCI.Channel("auto"),
            channels=UCI.Channels("36 40 44 48 100 104 108 112 116 120 124 128 132"),
            htmode=UCI.Htmode("VHT80"),
            country=UCI.Country("FR"),
            band=UCI.Band("5g"),
            disabled=0,
        )
        self.wireless_commands.append(self.radio0)
        self.radio1 = UCI.UCIWifiDevice(
            name=UCI.UCISectionName("radio1"),
            path=UCI.Path("platform/ahb/18100000.wmac"),
            device_type=UCI.WifiDeviceType("mac80211"),
            channel=UCI.Channel("auto"),
            htmode=UCI.Htmode("HT20"),
            country=UCI.Country("FR"),
            band=UCI.Band("2g"),
            disabled=0,
        )
        self.wireless_commands.append(self.radio1)

        # Dropbear Configuration
        self.dropbear_commands.append(UCI.UCIDropbear())


class HermesUser(ccb.HermesConfigBuilder):
    br_lan: UCI.UCIBridge
    lan_int: UCI.UCIInterface
    wan_int: UCI.UCIInterface
    wan6_int: UCI.UCIInterface
    route: UCI.UCIRoute
    route_rule: UCI.UCIRouteRule
    route6: UCI.UCIRoute6
    route6_rule: UCI.UCIRouteRule
    wifi_iface_0: UCI.UCIWifiIface
    wifi_iface_1: UCI.UCIWifiIface
    dhcp: UCI.UCIDHCP
    forwarding: UCI.UCIForwarding
    ping_rule: UCI.UCIRule
    snat: UCI.UCISnat

    def __init__(
        self,
        unetid: UCI.UNetId,
        ssid: UCI.SSID,
        wan_address: UCI.IPAddress,
        wan_netmask: UCI.IPAddress,
        wan6_address: UCI.IPAddress,
        lan_address: UCI.IPAddress,
        lan_network: UCI.IPNetwork,
        lan_main_prefix6: UCI.IPNetwork,
        lan_main_address6: UCI.IPAddress,
        unet6_prefix: UCI.IPNetwork,
        wifi_passphrase: UCI.WifiPassphrase,
        wan_vlan: int,
        wan6_vlan: int,
        lan_vlan: int,
        default_config: HermesDefaultConfig,
        default_router: UCI.IPAddress,
        default_router6: UCI.IPAddress,
    ):
        """Create a main user configuration

        Args:
            unetid (UCI.UNetId): The user netid
            ssid (UCI.SSID): The SSID of the user
            wan_address (UCI.IPAddress): The WAN address
            wan_netmask (UCI.IPAddress): The WAN netmask
            wan6_address (UCI.IPAddress): The WAN IPv6 address
            lan_address (UCI.IPAddress): The LAN address
            lan_network (UCI.IPNetwork): The LAN network
            lan6_prefix (UCI.IPNetwork): The LAN IPv6 prefix
            wifi_passphrase (UCI.WifiPassphrase): The wifi passphrase
            wan_vlan (int): The WAN VLAN
            wan6_vlan (int): The WAN IPv6 VLAN
            default_config (HermesDefaultConfig): The default configuration
            default_router (UCI.IPAddress): The default router
            default_router6 (UCI.IPAddress): The default IPv6 router
        """
        super().__init__()

        # Network Configuration
        self.lan_int = UCI.UCIInterface(
            name_prefix="lan_",
            ip=lan_address,
            mask=lan_network.netmask,
            proto=UCI.InterfaceProto("static"),
            unetid=unetid,
            device=self.br_lan,
        )
        self.network_commands.append(self.lan_int)

        self.lan_int = UCI.UCIInterface(
            name_prefix="lan_",
            ip=lan_address,
            ip6=lan_main_address6,
            mask=lan_network.netmask,
            proto=UCI.InterfaceProto("static"),
            unetid=unetid,
            device=self.br_lan,
        )
        self.network_commands.append(self.lan_int)

        self.wan_int = UCI.UCIInterface(
            unetid=unetid,
            name_prefix="wan_",
            ip=wan_address,
            mask=wan_netmask,
            proto=UCI.InterfaceProto("static"),
            device=UCI.UCISimpleDevice(f"eth0.{wan_vlan}"),
        )
        self.network_commands.append(self.wan_int)

        self.wan6_int = UCI.UCIInterface(
            unetid=unetid,
            name_prefix="wan6_",
            ip=wan6_address,
            mask=wan_netmask,
            proto=UCI.InterfaceProto("static"),
            device=UCI.UCISimpleDevice(f"eth0.{wan6_vlan}"),
        )
        self.network_commands.append(self.wan6_int)

        self.route = UCI.UCIRoute(
            unetid=unetid,
            name_prefix="route_default_wan_",
            target=UCI.IPNetwork("0.0.0.0/0"),
            gateway=default_router,
            interface=self.wan_int,
            table=int(f"1{str(lan_vlan).zfill(2)}"),
        )
        self.network_commands.append(self.route)

        self.route_rule = UCI.UCIRouteRule(
            unetid=unetid,
            src=lan_network,
            lookup=self.route.table,
        )
        self.network_commands.append(self.route_rule)

        self.route6 = UCI.UCIRoute6(
            unetid=unetid,
            name_prefix="route6_default_wan_",
            target=UCI.IPNetwork("::/0"),
            gateway=default_router6,
            interface=self.wan6_int,
            table=int(f"1{str(lan_vlan).zfill(2)}"),
        )
        self.network_commands.append(self.route6)

        self.route6_rule = UCI.UCIRouteRule(
            unetid=unetid,
            src=unet6_prefix,
            lookup=self.route6.table,
        )
        self.network_commands.append(self.route6_rule)

        # Wireless Configuration
        self.wifi_iface_0 = UCI.UCIWifiIface(
            unetid=unetid,
            device=default_config.radio0,
            mode=UCI.Mode("ap"),
            network=self.lan_int,
            ssid=ssid,
            encryption=UCI.Encryption("psk2"),
            passphrase=wifi_passphrase,
        )
        self.wireless_commands.append(self.wifi_iface_0)

        self.wifi_iface_0 = UCI.UCIWifiIface(
            unetid=unetid,
            device=default_config.radio1,
            mode=UCI.Mode("ap"),
            network=self.lan_int,
            ssid=ssid,
            encryption=UCI.Encryption("psk2"),
            passphrase=wifi_passphrase,
        )
        self.wireless_commands.append(self.wifi_iface_0)

        # DHCP Configuration
        self.dhcp = UCI.UCIDHCP(
            interface=self.lan_int, start=100, limit=150, leasetime=12
        )
        self.dhcp_commands.append(self.dhcp)

        # Firewall Configuration
        self.lan_zone = UCI.UCIZone(
            network=self.lan_int,
            _input=UCI.InOutForw("ACCEPT"),
            output=UCI.InOutForw("ACCEPT"),
            forward=UCI.InOutForw("REJECT"),
        )
        self.firewall_commands.append(self.lan_zone)
        self.wan_zone = UCI.UCIZone(
            network=self.wan_int,
            _input=UCI.InOutForw("REJECT"),
            output=UCI.InOutForw("ACCEPT"),
            forward=UCI.InOutForw("REJECT"),
            is_wan_zone=True,
        )
        self.firewall_commands.append(self.wan_zone)
        self.forwarding = UCI.UCIForwarding(src=self.lan_zone, dest=self.wan_zone)
        self.firewall_commands.append(self.forwarding)
        self.ping_rule = UCI.UCIRule(
            unetid=unetid,
            name=UCI.UCISectionName("wan_allow_ping"),
            desc=UCI.Description("Allow ping to WAN"),
            src=self.wan_zone,
            proto=UCI.Protocol("icmp"),
            icmp_type="echo-request",
            target=UCI.Target("ACCEPT"),
            family="ipv4",
        )
        self.firewall_commands.append(self.ping_rule)
        self.snat = UCI.UCISnat(
            wan_zone=self.wan_zone,
            lan_zone=self.lan_zone,
            wan_interface=self.wan_int,
            lan_interface=self.lan_int,
        )
        self.firewall_commands.append(self.snat)


class HermesMainUser(HermesUser):
    """Represents the main user configuration for the router
    Herits from HermesConfigBuilder
    """

    def __init__(
        self,
        unetid: UCI.UNetId,
        ssid: UCI.SSID,
        wan_address: UCI.IPAddress,
        wan_netmask: UCI.IPAddress,
        lan_address: UCI.IPAddress,
        lan_network: UCI.IPNetwork,
        wifi_passphrase: UCI.WifiPassphrase,
        wan_vlan: int,
        lan_vlan: int,
        default_config: HermesDefaultConfig,
        default_router: UCI.IPAddress,
    ):
        """Create a main user configuration

        Args:
            unetid (UCI.UNetId): The user netid
            ssid (UCI.SSID): The SSID of the user
            wan_address (UCI.IPAddress): The WAN address
            wan_netmask (UCI.IPAddress): The WAN netmask
            lan_address (UCI.IPAddress): The LAN address
            lan_network (UCI.IPNetwork): The LAN network
            wifi_passphrase (UCI.WifiPassphrase): The wifi passphrase
            wan_vlan (int): The WAN VLAN
            lan_vlan (int): The LAN VLAN
            default_config (HermesDefaultConfig): The default configuration
            default_router (UCI.IPAddress): The default router
        """
        self.lan_switch_vlan = UCI.UCISwitchVlan(
            UCI.UCISectionName(f"switch_vlan_{unetid}"),
            default_config.switch0,
            lan_vlan,
            UCI.UCINetworkPorts("2 3 4 0t"),
        )

        self.br_lan = UCI.UCIBridge(
            unetid=unetid,
            name_prefix=UCI.UCISectionNamePrefix("br_lan_"),
            ports=UCI.UCISimpleDevice(f"eth0.{lan_vlan}"),
        )

        super().__init__(
            unetid,
            ssid,
            wan_address,
            wan_netmask,
            lan_address,
            lan_network,
            wifi_passphrase,
            wan_vlan,
            lan_vlan,
            default_config,
            default_router,
        )
        self.network_commands.append(self.lan_switch_vlan)
        self.network_commands.append(self.br_lan)


class HermesSecondaryUser(HermesUser):
    """Same as HermesMainUser but with a different default bridge"""

    lan_switch_vlan: UCI.UCISwitchVlan

    def __init__(
        self,
        unetid: UCI.UNetId,
        ssid: UCI.SSID,
        wan_address: UCI.IPAddress,
        wan_netmask: UCI.IPAddress,
        lan_address: UCI.IPAddress,
        lan_network: UCI.IPNetwork,
        wifi_passphrase: UCI.WifiPassphrase,
        wan_vlan: int,
        lan_vlan: int,
        default_config: HermesDefaultConfig,
        default_router: UCI.IPAddress,
    ):
        """Create a secondary user configuration

        Args:
            unetid (UCI.UNetId): The user netid
            ssid (UCI.SSID): The SSID of the user
            wan_address (UCI.IPAddress): The WAN address
            wan_netmask (UCI.IPAddress): The WAN netmask
            lan_address (UCI.IPAddress): The LAN address
            lan_network (UCI.IPNetwork): The LAN network
            wifi_passphrase (UCI.WifiPassphrase): The wifi passphrase
            wan_vlan (int): The WAN VLAN
            lan_vlan (int): The LAN VLAN
            default_config (HermesDefaultConfig): The default configuration
            default_router (UCI.IPAddress): The default router
        """
        self.lan_switch_vlan = UCI.UCISwitchVlan(
            name=UCI.UCISectionName(f"switch_vlan_{unetid}"),
            device=default_config.switch0,
            vid=lan_vlan,
            ports=UCI.UCINetworkPorts("0t"),
        )
        self.br_lan = UCI.UCIBridge(
            unetid=unetid,
            name_prefix=UCI.UCISectionNamePrefix("br_lan_"),
            ports=UCI.UCISimpleDevice(f"eth0.{lan_vlan}"),
        )
        super().__init__(
            unetid,
            ssid,
            wan_address,
            wan_netmask,
            lan_address,
            lan_network,
            wifi_passphrase,
            wan_vlan,
            lan_vlan,
            default_config,
            default_router,
        )
        self.network_commands.append(self.lan_switch_vlan)
        self.network_commands.append(self.br_lan)


class HermesPortForwarding(ccb.HermesConfigBuilder):
    """Represents a port forwarding configuration
    Herits from HermesConfigBuilder
    """

    port_forwarding: UCI.UCIRedirect4

    def __init__(
        self,
        unetid: UCI.UNetId,
        name: UCI.UCISectionName,
        desc: UCI.Description,
        src_dport: UCI.TCPUDPPort,
        dest: UCI.UCIZone,
        dest_ip: UCI.IPAddress,
        dest_port: UCI.TCPUDPPort,
        proto: UCI.Protocol,
        src_dip: UCI.IPAddress = None,
        src: UCI.UCIZone = None,
        src_ip: UCI.IPAddress = None,
    ):
        """Create a port forwarding configuration

        Args:
            unetid (UCI.UNetId): The user netid
            name (UCI.UCISectionName): The name of the port forwarding
            desc (UCI.Description): The description of the port forwarding
            src (UCI.UCIZone): The source interface
            src_dport (UCI.TCPUDPPort): The source port
            dest (UCI.UCIZone): The destination interface
            dest_ip (UCI.IPAddress): The destination IP
            dest_port (UCI.TCPUDPPort): The destination port
            proto (UCI.Protocol): The protocol
            src_ip (UCI.IPAddress, optional): The source IP. Defaults to None."""
        super().__init__()
        self.port_forwarding = UCI.UCIRedirect4(
            unetid=unetid,
            name=name,
            desc=desc,
            src=src,
            src_dip=src_dip,
            src_ip=src_ip,
            src_dport=src_dport,
            dest=dest,
            dest_ip=dest_ip,
            dest_port=dest_port,
            proto=proto,
        )
        self.firewall_commands.append(self.port_forwarding)


if __name__ == "__main__":
    # Testing the HermesConfigBuilder
    # To run in standalone mode python -m hermes.hermes_command_building.ac2350

    Netconf = ccb.UCINetworkConfig()
    Fireconf = ccb.UCIFirewallConfig()
    Dhcpconf = ccb.UCIDHCPConfig()
    Wirelessconf = ccb.UCIWirelessConfig()
    Dropbearconf = ccb.UCIDropbearConfig()

    defconf = HermesDefaultConfig(UCI.DnsServers([UCI.IPAddress("8.8.8.8")]))

    defconf.build_network(Netconf)
    defconf.build_firewall(Fireconf)
    defconf.build_dhcp(Dhcpconf)
    defconf.build_wireless(Wirelessconf)
    defconf.build_dropbear(Dropbearconf)

    # Print the default configuration
    PRINTDEF = False
    if PRINTDEF is True:
        print("------ DEFAULT CONFIGURATION ------")
        print(Netconf.build())
        print(Fireconf.build())
        print(Dhcpconf.build())
        print(Wirelessconf.build())
        print(Dropbearconf.build())
        print("------ END DEFAULT CONFIGURATION ------")

    main_user = HermesMainUser(
        unetid=UCI.UNetId("aaaaaaaa"),
        ssid=UCI.SSID("Rezel-main"),
        wan_address=UCI.IPAddress("137.194.8.2"),
        wan_netmask=UCI.IPAddress("255.255.252.0"),
        lan_address=UCI.IPAddress("192.168.0.1"),
        lan_network=UCI.IPNetwork("192.168.0.0/24"),
        wifi_passphrase=UCI.WifiPassphrase("password"),
        wan_vlan=101,
        lan_vlan=1,
        default_config=defconf,
        default_router=UCI.IPAddress("137.194.11.254"),
    )

    main_user.build_network(Netconf)
    main_user.build_firewall(Fireconf)
    main_user.build_dhcp(Dhcpconf)
    main_user.build_wireless(Wirelessconf)

    secondary_user = HermesSecondaryUser(
        unetid=UCI.UNetId("bbbbbbbb"),
        ssid=UCI.SSID("Rezel-secondary"),
        wan_address=UCI.IPAddress("195.14.28.2"),
        wan_netmask=UCI.IPAddress("255.255.255.0"),
        lan_address=UCI.IPAddress("192.168.1.1"),
        lan_network=UCI.IPNetwork("192.168.1.0/24"),
        wifi_passphrase=UCI.WifiPassphrase("password"),
        wan_vlan=102,
        lan_vlan=2,
        default_config=defconf,
        default_router=UCI.IPAddress("195.14.28.1"),
    )
    secondary_user.build_network(Netconf)
    secondary_user.build_firewall(Fireconf)
    secondary_user.build_dhcp(Dhcpconf)
    secondary_user.build_wireless(Wirelessconf)

    tertiary_user = HermesSecondaryUser(
        unetid=UCI.UNetId("cccccccc"),
        ssid=UCI.SSID("Rezel-tertiary"),
        wan_address=UCI.IPAddress("137.194.8.3"),
        wan_netmask=UCI.IPAddress("255.255.252.0"),
        lan_address=UCI.IPAddress("192.168.2.1"),
        lan_network=UCI.IPNetwork("192.168.2.0/24"),
        wifi_passphrase=UCI.WifiPassphrase("password"),
        wan_vlan=101,
        lan_vlan=3,
        default_config=defconf,
        default_router=UCI.IPAddress("137.194.11.254"),
    )
    tertiary_user.build_network(Netconf)
    tertiary_user.build_firewall(Fireconf)
    tertiary_user.build_dhcp(Dhcpconf)
    tertiary_user.build_wireless(Wirelessconf)

    main_port_forwarding = HermesPortForwarding(
        unetid=UCI.UNetId("aaaaaaaa"),
        name=UCI.UCISectionName("http_to_internal"),
        desc=UCI.Description("HTTP forwarding"),
        src=main_user.wan_zone,
        src_dport=UCI.TCPUDPPort(80),
        dest=main_user.lan_zone,
        dest_ip=UCI.IPAddress("192.168.0.5"),
        dest_port=UCI.TCPUDPPort(80),
        proto=UCI.Protocol("tcp"),
    )
    main_port_forwarding.build_firewall(Fireconf)

    print(Netconf.build())
    print(Fireconf.build())
    print(Dhcpconf.build())
    print(Wirelessconf.build())
    print(Dropbearconf.build())
