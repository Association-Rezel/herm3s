# import uci_common as UCI
import hermes_config_building.uci_common as UCI  # to import from communication_deamon


class UCITypeConfig:
    """Mother class reprensenting a config block uci
    (e.g. network, firewall, dhcp, wireless, dropbear)
    """

    commands: str

    def __init__(self):
        pass

    def build(self) -> str:
        """Add the reload commands to the config block

        Returns:
            str: Config block with reload command
        """


class UCINetworkConfig(UCITypeConfig):
    """Represents the network configuration block in UCI"""

    def __init__(self):
        self.commands = ""

    def build(self) -> str:
        return self.commands + "uci commit\nservice network restart\n"


class UCIFirewallConfig(UCITypeConfig):
    """Represents the firewall configuration block in UCI"""

    def __init__(self):
        self.commands = ""

    def build(self) -> str:
        return self.commands + "uci commit\nservice firewall restart\n"


class UCIDHCPConfig(UCITypeConfig):
    """Represents the DHCP configuration block in UCI"""

    def __init__(self):
        self.commands = ""

    def build(self) -> str:
        return self.commands + "uci commit\nservice dnsmasq restart\n"


class UCIWirelessConfig(UCITypeConfig):
    """Represents the wireless configuration block in UCI"""

    def __init__(self):
        self.commands = ""

    def build(self) -> str:
        return self.commands + "uci commit\nwifi reload\n"


class UCIDropbearConfig(UCITypeConfig):
    """Represents the dropbear configuration block in UCI"""

    def __init__(self):
        self.commands = ""

    def build(self) -> str:
        return self.commands + "uci commit\nservice dropbear restart\n"


class HermesConfigBuilder:
    """Mother class for the configuration builders
    The commands lists contain blocks of UCI commands
    That can be call with uci_build_string() to get the string
    """

    network_commands: list[UCI.UCIConfig]
    firewall_commands: list[UCI.UCIConfig]
    dhcp_commands: list[UCI.UCIConfig]
    wireless_commands: list[UCI.UCIConfig]
    dropbear_commands: list[UCI.UCIConfig]

    def __init__(self):
        self.network_commands = []
        self.firewall_commands = []
        self.dhcp_commands = []
        self.wireless_commands = []
        self.dropbear_commands = []

    def build_network(self, network: UCINetworkConfig) -> UCINetworkConfig:
        for uci_config in self.network_commands:
            network.commands += uci_config.uci_build_string()
        return network

    def build_firewall(self, firewall: UCIFirewallConfig) -> UCIFirewallConfig:
        for uci_config in self.firewall_commands:
            firewall.commands += uci_config.uci_build_string()
        return firewall

    def build_dhcp(self, dhcp: UCIDHCPConfig) -> UCIDHCPConfig:
        for uci_config in self.dhcp_commands:
            dhcp.commands += uci_config.uci_build_string()
        return dhcp

    def build_wireless(self, wireless: UCIWirelessConfig) -> UCIWirelessConfig:
        for uci_config in self.wireless_commands:
            wireless.commands += uci_config.uci_build_string()
        return wireless

    def build_dropbear(self, dropbear: UCIDropbearConfig) -> UCIDropbearConfig:
        for uci_config in self.dropbear_commands:
            dropbear.commands += uci_config.uci_build_string()
        return dropbear


class HermesDefaultConfig(HermesConfigBuilder):
    """Mother class for the default configuration of the router
    Herits from HermesConfigBuilder
    """

    loopback: UCI.UCIInterface
    switch0: UCI.UCISwitch
    vlan_1: UCI.UCISwitchVlan
    vlan_65: UCI.UCISwitchVlan
    vlan_101: UCI.UCISwitchVlan
    vlan_102: UCI.UCISwitchVlan
    management: UCI.UCINoIPInterface
    radio0: UCI.UCIWifiDevice
    radio1: UCI.UCIWifiDevice


class HermesAC2350DefaultConfig(HermesDefaultConfig):
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
        self.vlan_1 = UCI.UCISwitchVlan(
            UCI.UCISectionName("vlan_1"),
            self.switch0,
            1,
            UCI.UCINetworkPorts("2 3 4 0t"),
        )
        self.network_commands.append(self.vlan_1)
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
            channel=36,
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
            channel=1,
            htmode=UCI.Htmode("HT20"),
            country=UCI.Country("FR"),
            band=UCI.Band("2g"),
            disabled=0,
        )
        self.wireless_commands.append(self.radio1)

        # Dropbear Configuration
        self.dropbear_commands.append(UCI.UCIDropbear())


class HermesUser(HermesConfigBuilder):
    br_lan: UCI.UCIBridge
    lan_int: UCI.UCIInterface
    wan_int: UCI.UCIInterface
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
            default_config (HermesDefaultConfig): The default configuration
            default_router (UCI.IPAddress): The default router
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

        self.wan_int = UCI.UCIInterface(
            unetid=unetid,
            name_prefix="wan_",
            ip=wan_address,
            mask=wan_netmask,
            proto=UCI.InterfaceProto("static"),
            device=UCI.UCISimpleDevice(f"eth0.{wan_vlan}"),
        )
        self.network_commands.append(self.wan_int)

        self.network_commands.append(
            UCI.UCIRoute(
                unetid=unetid,
                name_prefix="route_default_wan_",
                target=UCI.IPNetwork("0.0.0.0/0"),
                gateway=default_router,
                interface=self.wan_int,
            )
        )

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
            default_config (HermesDefaultConfig): The default configuration
            default_router (UCI.IPAddress): The default router
        """
        self.br_lan = UCI.UCIBridge(
            unetid=unetid,
            name_prefix=UCI.UCISectionNamePrefix("br_lan_"),
            ports=UCI.UCISimpleDevice("eth0.1"),
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
            default_config,
            default_router,
        )
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
            default_config,
            default_router,
        )
        self.network_commands.append(self.lan_switch_vlan)
        self.network_commands.append(self.br_lan)


class HermesPortForwarding(HermesConfigBuilder):
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
        unetid=UCI.UNetId("aaaaaaaa"),
        ssid=UCI.SSID("Rezel-main"),
        wan_address=UCI.IPAddress("137.194.8.2"),
        wan_netmask=UCI.IPAddress("255.255.248.0"),
        lan_address=UCI.IPAddress("192.168.0.1"),
        lan_network=UCI.IPNetwork("192.168.0.0/24"),
        wifi_passphrase=UCI.WifiPassphrase("password"),
        wan_vlan=101,
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
        default_router=UCI.IPAddress("195.14.28.254"),
    )
    secondary_user.build_network(Netconf)
    secondary_user.build_firewall(Fireconf)
    secondary_user.build_dhcp(Dhcpconf)
    secondary_user.build_wireless(Wirelessconf)

    tertiary_user = HermesSecondaryUser(
        unetid=UCI.UNetId("cccccccc"),
        ssid=UCI.SSID("Rezel-tertiary"),
        wan_address=UCI.IPAddress("137.194.8.3"),
        wan_netmask=UCI.IPAddress("255.255.248.0"),
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
