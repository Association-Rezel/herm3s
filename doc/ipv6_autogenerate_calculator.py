from netaddr import EUI
from ipaddress import IPv6Interface, IPv6Network


def get_slaac_from_mac(mac: EUI, prefix: IPv6Network):
    host_id = mac.modified_eui64()
    address_binary = int(host_id) + int(prefix.network_address)

    return IPv6Interface(address_binary)


print(get_slaac_from_mac(EUI("0c:3c:70:c4:00:00"), IPv6Network("fd5d:fa1:fa1:1::/64")))
