from ipaddress import IPv4Address, IPv6Address
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from netaddr import EUI, AddrFormatError, mac_unix_expanded

from hermes.env import ENV
from hermes.hermes_command_building import ac2350
from hermes.hermes_command_building import common_command_builder as ccb
from hermes.hermes_command_building import uci_common as UCI
from hermes.mongodb.db import get_box_by_mac, get_db
from hermes.mongodb.models import Box, UnetProfile

router = APIRouter()


# download file from hermes to box
@router.get("/v1/config/ac2350/{mac}")
async def ac2350_get_file_config_init(mac: str, db=Depends(get_db)):
    """
    Download the configuration file for the box with the mac address mac
    args:
        mac: str: mac address of the box
    """
    try:
        mac_box = EUI(mac)
        mac_box.dialect = mac_unix_expanded
    except AddrFormatError as e:
        raise HTTPException(
            400, {"Erreur": "invalid mac address", "details": str(e)}
        ) from e
    try:
        create_configfile(await get_box_by_mac(db, mac_box))
    except ValueError as e:
        logging.error("Error: %s", str(e))
        raise HTTPException(404, {"Erreur": str(e)}) from e
    return FileResponse(
        f"{ENV.temp_generated_box_configs_dir}configfile_" + str(mac_box) + ".txt",
        filename="configfile.txt",
    )


@router.get("/v1/config/ac2350/default/file")
async def ac2350_get_default_config():
    """
    Download the default configuration file
    """
    create_default_configfile()
    return FileResponse(
        f"{ENV.temp_generated_box_configs_dir}defaultConfigfile.txt",
        filename="defaultConfigfile.txt",
    )


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

    unets: list[UnetProfile] = []

    for unet in box.unets:
        if unet.unet_id == main_user_unetid:
            unets.insert(0, unet)
        else:
            unets.append(unet)

    for unet in unets:

        wan_ip_address = unet.network.wan_ipv4.ip
        lan_ip_address = unet.network.lan_ipv4.address

        default_router_v6: Optional[IPv6Address]
        for wan_vlan in box.wan_vlan:
            if wan_vlan.vlan_id == unet.network.wan_ipv6.vlan:
                default_router_v6 = wan_vlan.ipv6_gateway
                break
        if default_router_v6 is None:
            raise ValueError(
                f"Error: No matching VLAN found for {unet.network.wan_ipv6.vlan}"
            )

        user: ac2350.HermesUser
        main_user: ac2350.HermesMainUser
        if unet.unet_id == main_user_unetid:
            # Get the default router for the main user (not needed for secondary users bc it's shared)
            default_router_v4: Optional[IPv4Address]
            for wan_vlan in box.wan_vlan:
                if wan_vlan.vlan_id == unet.network.wan_ipv4.vlan:
                    default_router_v4 = wan_vlan.ipv4_gateway
                    break
            if default_router_v4 is None:
                raise ValueError(
                    f"Error: No matching VLAN found for {unet.network.wan_ipv4.vlan}"
                )

            user = ac2350.HermesMainUser(
                unetid=UCI.UNetId(unet.unet_id),
                ssid=UCI.SSID(unet.wifi.ssid),
                wan_address=wan_ip_address,
                lan_address=lan_ip_address,
                wifi_passphrase=UCI.WifiPassphrase(unet.wifi.psk),
                dns_servers_v4=UCI.DnsServers(unet.dhcp.dns_servers.ipv4),
                dns_servers_v6=UCI.DnsServers(unet.dhcp.dns_servers.ipv6),
                wan_vlan=unet.network.wan_ipv4.vlan,
                lan_vlan=unet.network.lan_ipv4.vlan,
                default_config=defconf,
                default_router=default_router_v4,
                wan6_address=unet.network.wan_ipv6.ip,
                unet6_prefix=unet.network.ipv6_prefix,
                wan6_vlan=unet.network.wan_ipv6.vlan,
                default_router6=default_router_v6,
            )
            main_user = user
        else:
            user = ac2350.HermesSecondaryUser(
                unetid=UCI.UNetId(unet.unet_id),
                ssid=UCI.SSID(unet.wifi.ssid),
                wan_address=wan_ip_address,
                lan_address=lan_ip_address,
                lan_vlan=unet.network.lan_ipv4.vlan,
                wifi_passphrase=UCI.WifiPassphrase(unet.wifi.psk),
                dns_servers_v4=UCI.DnsServers(unet.dhcp.dns_servers.ipv4),
                dns_servers_v6=UCI.DnsServers(unet.dhcp.dns_servers.ipv6),
                wan_vlan=unet.network.wan_ipv4.vlan,
                default_config=defconf,
                wan6_address=unet.network.wan_ipv6.ip,
                unet6_prefix=unet.network.ipv6_prefix,
                wan6_vlan=unet.network.wan_ipv6.vlan,
                default_router6=default_router_v6,
                hermes_primary_user=main_user,
            )

        user.build_network(Netconf)
        user.build_firewall(Fireconf)
        user.build_dhcp(Dhcpconf)
        user.build_wireless(Wirelessconf)

        # Create port forwardings
        for port_forwarding in unet.firewall.ipv4_port_forwarding:
            user_port_forwarding = ac2350.HermesPortForwarding(
                unetid=UCI.UNetId(unet.unet_id),
                name=UCI.UCISectionName(
                    f"port_forwarding_dport_{port_forwarding.wan_port}"
                ),
                desc=UCI.Description(
                    f"port_forwarding_dport_{port_forwarding.wan_port}"
                ),
                src=user.wan_zone,
                src_dport=UCI.TCPUDPPort(port_forwarding.wan_port),
                dest=user.lan_zone,
                dest_ip=port_forwarding.lan_ip,
                dest_port=UCI.TCPUDPPort(port_forwarding.lan_port),
                proto=UCI.Protocol(port_forwarding.protocol),
            )
            user_port_forwarding.build_firewall(Fireconf)

        # BOUCLE POUR L'OUVERTURE DES PORTS IPV6
        for ipv6_rule in unet.firewall.ipv6_port_opening:
            user_ipv6_opening = ac2350.HermesIPv6PortOpening(
                unetid=UCI.UNetId(unet.unet_id),
                name=UCI.UCISectionName(f"ipv6_open_dport_{ipv6_rule.port}"),
                desc=UCI.Description(
                    f"Allow IPv6 to {ipv6_rule.ip} on port {ipv6_rule.port}"
                ),
                src=user.wan6_zone,
                dest=user.lan_zone,
                dest_ip=ipv6_rule.ip,
                dest_port=UCI.TCPUDPPort(ipv6_rule.port),
                proto=UCI.Protocol(ipv6_rule.protocol),
            )
            user_ipv6_opening.build_firewall(Fireconf)

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
