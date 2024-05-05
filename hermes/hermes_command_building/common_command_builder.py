from .uci_common import uci_common as UCI

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


