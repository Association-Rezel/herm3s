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
            name=UCI.UCISectionName("management"),
            device=UCI.UCISimpleDevice("eth0.65"),
            proto=UCI.InterfaceProto("dhcpv6"),
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

        self.mgt_zone = UCI.UCIZone(
            network=self.management,
            _input=UCI.InOutForw("REJECT"),
            output=UCI.InOutForw("ACCEPT"),
            forward=UCI.InOutForw("REJECT"),
        )
        self.firewall_commands.append(self.mgt_zone)

        self.rule_icmpv6_mgt = UCI.UCIRule(
            unetid="managemen",
            name=UCI.UCISectionName("mgt_allow_ping"),
            desc=UCI.Description("Allow ICMPv6 to MGT"),
            src=self.mgt_zone,
            proto=UCI.Protocol("icmp"),
            target=UCI.Target("ACCEPT"),
            family="ipv6",
        )
        self.firewall_commands.append(self.rule_icmpv6_mgt)

        self.rule_ssh_mgt = UCI.UCIRule(
            unetid="managemen",
            name=UCI.UCISectionName("mgt_allow_ssh"),
            desc=UCI.Description("Allow ssh to MGT"),
            src=self.mgt_zone,
            dest_port=UCI.TCPUDPPort(22),
            proto=UCI.Protocol("tcp"),
            target=UCI.Target("ACCEPT"),
            family="ipv6",
        )
        self.firewall_commands.append(self.rule_ssh_mgt)

        self.rule_daemon_mgt = UCI.UCIRule(
            unetid="managemen",
            name=UCI.UCISectionName("mgt_allow_daemon"),
            desc=UCI.Description("Allow deamon to MGT"),
            src=self.mgt_zone,
            dest_port=UCI.TCPUDPPort(50051),
            proto=UCI.Protocol("tcp"),
            target=UCI.Target("ACCEPT"),
            family="ipv6",
        )
        self.firewall_commands.append(self.rule_daemon_mgt)

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
    """Represents a user configuration for the router
    Herits from HermesConfigBuilder
    """

    unetid: UCI.UNetId
    lan_vlan: int
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
        lan_address: UCI.IPAddress,
        lan_network: UCI.IPNetwork,
        wifi_passphrase: UCI.WifiPassphrase,
        wan_vlan: int,
        lan_vlan: int,
        default_config: HermesDefaultConfig,
        default_router: UCI.IPAddress,
        wan6_address: UCI.IPNetwork,
        unet6_prefix: UCI.IPNetwork,
        wan6_vlan: int,
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
        self.unetid = unetid
        self.lan_vlan = lan_vlan

        # Network Configuration

        self.wan_int = UCI.UCIInterface(
            unetid=unetid,
            name_prefix="wan_",
            ip=wan_address,
            mask=wan_netmask,
            proto=UCI.InterfaceProto("static"),
            device=UCI.UCISimpleDevice(f"eth0.{wan_vlan}"),
        )
        self.network_commands.append(self.wan_int)

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
            name=UCI.UCISectionName(f"route_rule_{unetid}"),
            src=lan_network,
            lookup=self.route.table,
        )
        self.network_commands.append(self.route_rule)

        self.wan6_int = UCI.UCIInterface(
            unetid=unetid,
            name_prefix="wan6_",
            ip6addr=wan6_address,
            ip6gw=default_router6,
            ip6prefix=unet6_prefix,
            proto=UCI.InterfaceProto("static"),
            device=UCI.UCISimpleDevice(f"eth0.{wan6_vlan}"),
        )
        self.network_commands.append(self.wan6_int)

        self.route6 = UCI.UCIRoute(
            unetid=unetid,
            name_prefix="route6_default_wan_",
            target=UCI.IPNetwork("::/0"),
            gateway=default_router6,
            interface=self.wan6_int,
            table=int(f"1{str(lan_vlan).zfill(2)}"),
        )
        self.network_commands.append(self.route6)

        self.route6_rule = UCI.UCIRouteRule(
            name=UCI.UCISectionName(f"route6_rule_{unetid}"),
            src=unet6_prefix,
            lookup=self.route6.table,
        )
        self.network_commands.append(self.route6_rule)

        self.lan_int = UCI.UCIInterface(
            name_prefix="lan_",
            ip=lan_address,
            mask=lan_network.netmask,
            proto=UCI.InterfaceProto("static"),
            unetid=unetid,
            device=self.br_lan,
            ip6class=self.wan6_int.name,
            ip6assign=64,
        )
        self.network_commands.append(self.lan_int)

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
            family=UCI.Family("any"),
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

        self.wan6_zone = UCI.UCIZone(
            network=self.wan6_int,
            _input=UCI.InOutForw("REJECT"),
            output=UCI.InOutForw("ACCEPT"),
            forward=UCI.InOutForw("REJECT"),
            family=UCI.Family("ipv6"),
        )
        self.firewall_commands.append(self.wan6_zone)

        self.forwarding6 = UCI.UCIForwarding(
            src=self.lan_zone,
            dest=self.wan6_zone,
        )
        self.firewall_commands.append(self.forwarding6)

        self.rule_icmpv6_wan6 = UCI.UCIRule(
            unetid=unetid,
            name=UCI.UCISectionName("wan6_allow_ping"),
            desc=UCI.Description("Allow ICMPv6 to WAN6"),
            src=self.wan6_zone,
            proto=UCI.Protocol("icmp"),
            target=UCI.Target("ACCEPT"),
            family="ipv6",
        )
        self.firewall_commands.append(self.rule_icmpv6_wan6)


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
        wan6_address: UCI.IPNetwork,
        unet6_prefix: UCI.IPNetwork,
        wan6_vlan: int,
        default_router6: UCI.IPAddress,
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
            unetid=unetid,
            ssid=ssid,
            wan_address=wan_address,
            wan_netmask=wan_netmask,
            lan_address=lan_address,
            lan_network=lan_network,
            wifi_passphrase=wifi_passphrase,
            wan_vlan=wan_vlan,
            lan_vlan=lan_vlan,
            default_config=default_config,
            default_router=default_router,
            wan6_address=wan6_address,
            unet6_prefix=unet6_prefix,
            wan6_vlan=wan6_vlan,
            default_router6=default_router6,
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
        wan6_address: UCI.IPNetwork,
        unet6_prefix: UCI.IPNetwork,
        wan6_vlan: int,
        default_router6: UCI.IPAddress,
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
            unetid=unetid,
            ssid=ssid,
            wan_address=wan_address,
            wan_netmask=wan_netmask,
            lan_address=lan_address,
            lan_network=lan_network,
            wifi_passphrase=wifi_passphrase,
            wan_vlan=wan_vlan,
            lan_vlan=lan_vlan,
            default_config=default_config,
            default_router=default_router,
            wan6_address=wan6_address,
            unet6_prefix=unet6_prefix,
            wan6_vlan=wan6_vlan,
            default_router6=default_router6,
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


class HermesIPv6PortOpening(ccb.HermesConfigBuilder):
    """Represents a port opening configuration for IPv6"""

    ipv6_port_opening: UCI.UCIRule

    def __init__(
        self,
        unetid: UCI.UNetId,
        name: UCI.UCISectionName,
        desc: UCI.Description,
        src: UCI.UCIZone,
        dest: UCI.UCIZone,
        dest_ip: UCI.IPAddress,
        dest_port: UCI.TCPUDPPort,
        proto: UCI.Protocol,
    ):
        super().__init__()
        self.ipv6_port_opening = UCI.UCIRule(
            unetid=unetid,
            name=name,
            desc=desc,
            src=src,
            dest=dest,
            dest_ip=dest_ip,
            dest_port=dest_port,
            proto=proto,
            target=UCI.Target("ACCEPT"),
            family="ipv6",
        )
        self.firewall_commands.append(self.ipv6_port_opening)


# For the next 3 classes: its work in progress
class HermesStaticDHCPLease(ccb.HermesConfigBuilder):
    """Represents a static DHCP lease configuration"""

    static_dhcp_lease: UCI.UCIHost

    def __init__(
        self,
        unetid: UCI.UNetId,
        hostname: str,
        ip: UCI.IPAddress = None,
        mac: UCI.EUI = None,
        hostid: str = None,
        duid: UCI.DUid = None,
    ):
        super().__init__()
        self.static_dhcp_lease = UCI.UCIHost(
            unetid=unetid,
            hostname=hostname,
            ip=ip,
            mac=mac,
            hostid=hostid,
            duid=duid,
        )
        self.dhcp_commands.append(self.static_dhcp_lease)


class HermesDynIPv6PrefDelegation(ccb.HermesConfigBuilder):
    """
    Represents a IPv6 prefix delegation configuration
    See https://openwrt.org/docs/guide-user/firewall/fw3_configurations/fw3_ipv6_examples#dynamic_prefix_forwarding
    """

    ipv6_pref_delegation: UCI.UCIRule

    def __init__(
        self,
        associated_lease: HermesStaticDHCPLease,
        unetid: UCI.UNetId,
        name: UCI.UCISectionName,
        desc: UCI.Description,
        src: UCI.UCIZone,
        dest: UCI.UCIZone,
        proto: UCI.Protocol = "tcp udp icmp",
    ):
        super().__init__()
        self.ipv6_pref_delegation = UCI.UCIRule(
            unetid=unetid,
            name=name,
            desc=desc,
            src=src,
            dest=dest,
            proto=proto,
            dest_ip=f"::{associated_lease.static_dhcp_lease.ip}/-64",
            target=UCI.Target("ACCEPT"),
            family="ipv6",
        )
        self.firewall_commands.append(self.ipv6_pref_delegation)


class HermesStaticIPv6PrefDelegation(ccb.HermesConfigBuilder):
    """
    Represents a static IPv6 prefix delegation configuration
    """

    def __init__(
        self,
        name: UCI.UCISectionName,
        user: HermesUser,
        dest_router: UCI.IPAddress,
        prefix: UCI.IPNetwork,
    ):
        super().__init__()

        self.route6 = UCI.UCIRoute(
            unetid=user.unetid,
            name_prefix=name,
            target=prefix,
            gateway=dest_router,
            interface=user.lan_int,
            table=int(f"7{str(user.lan_vlan).zfill(2)}"),
        )
        self.network_commands.append(self.route6)

        self.route6_rule = UCI.UCIRouteRule(
            name=UCI.UCISectionName(f"{user.unetid}_{name}_rule"),
            dest=prefix,
            lookup=self.route6.table,
        )
        self.network_commands.append(self.route6_rule)

        self.ipset = UCI.UCIIpset(
            name=UCI.UCISectionName(f"{user.unetid}_set_{name}"),
            match=UCI.MatchIPSet("net_dest"),
            entry=[UCI.IPNetwork(prefix)],
        )
        self.firewall_commands.append(self.ipset)

        self.forwarding = UCI.UCIForwarding(
            src=user.wan6_zone,
            dest=user.lan_zone,
            ipset=self.ipset,
            optional_name_suffix=name,
        )
        self.firewall_commands.append(self.forwarding)


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
    # def router 2a09:6847:ffff::1/64
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
        wan6_address=UCI.IPNetwork("2a09:6847:ffff::0802/64"),
        unet6_prefix=UCI.IPNetwork("2a09:6847:0802::/48"),
        wan6_vlan=103,
        default_router6=UCI.IPAddress("2a09:6847:ffff::1"),
    )
    # route 2a09:6847:0802::/48 via 2a09:6847:ffff::0802;
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
        wan6_address=UCI.IPNetwork("2a09:6847:ffff::0402/64"),
        unet6_prefix=UCI.IPNetwork("2a09:6847:0402::/48"),
        wan6_vlan=103,
        default_router6=UCI.IPAddress("2a09:6847:ffff::1"),
    )
    # route 2a09:6847:0402::/48 via 2a09:6847:ffff::0402;
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
        wan6_address=UCI.IPNetwork("2a09:6847:ffff::0803/64"),
        unet6_prefix=UCI.IPNetwork("2a09:6847:0803::/48"),
        wan6_vlan=103,
        default_router6=UCI.IPAddress("2a09:6847:ffff::1"),
    )
    # route 2a09:6847:0803::/48 via 2a09:6847:ffff::0803;
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

    ipv6_port_opening = HermesIPv6PortOpening(
        unetid=UCI.UNetId("bbbbbbbb"),
        name=UCI.UCISectionName("http_to_internal_ipv6"),
        desc=UCI.Description("HTTP IPv6 Opening"),
        src=secondary_user.wan6_zone,
        dest=secondary_user.lan_zone,
        dest_ip=UCI.IPAddress("2a09:6847:402:0:ee2:7ff:fe59:0"),
        dest_port=UCI.TCPUDPPort(80),
        proto=UCI.Protocol("tcp"),
    )
    ipv6_port_opening.build_firewall(Fireconf)

    # static_dhcp_lease = HermesStaticDHCPLease(
    #     unetid=UCI.UNetId("bbbbbbbb"),
    #     hostname="test",
    #     hostid="24",
    #     mac=UCI.EUI("0c:7b:2c:7e:00:00"),
    # )
    # static_dhcp_lease.build_dhcp(Dhcpconf)

    # ipv6_pref_delegation = HermesDynIPv6PrefDelegation(
    #     associated_lease=static_dhcp_lease,
    #     unetid=UCI.UNetId("bbbbbbbb"),
    #     name=UCI.UCISectionName("ipv6_pref_delegation"),
    #     desc=UCI.Description("IPv6 prefix delegation"),
    #     src=secondary_user.wan6_zone,
    #     dest=secondary_user.lan_zone,
    # )
    # ipv6_pref_delegation.build_firewall(Fireconf)

    static_ipv6_pref_delegation = HermesStaticIPv6PrefDelegation(
        name=UCI.UCISectionName("ip6_pref_deleg_1"),
        user=secondary_user,
        dest_router=UCI.IPAddress("2a09:6847:402:0:ee2:7ff:fe59:0"),
        prefix=UCI.IPNetwork("2a09:6847:0402:3::/64"),
    )
    static_ipv6_pref_delegation.build_network(Netconf)
    static_ipv6_pref_delegation.build_firewall(Fireconf)

    print(Netconf.build())
    print(Fireconf.build())
    print(Dhcpconf.build())
    print(Wirelessconf.build())
    print(Dropbearconf.build())
