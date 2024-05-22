"""
This module contains the functions to generate the query strings for the Netbox API
"""


def camel_to_snake(string: str):
    """convert a camelCase string to snake_case while preserving
      the integrity of the MAC addresses in the string

    Args :
        string (str) : the string to convert to snake_case"""
    result = []
    is_previous_previous_colon = False
    is_previous_colon = False
    for c in string[1:]:
        if c.isupper() and not is_previous_colon and not is_previous_previous_colon:
            result.append("_")
            result.append(c.lower())
        else:
            is_previous_previous_colon = is_previous_colon
            is_previous_colon = c == ":"
            result.append(c)
    return string[0] + "".join(result)

def create_query_interface(mac: str) -> str:
    """create a query string to get the informations about a box from its MAC address

    Args :
        mac (str) : the MAC address of the box"""
    query = """
{
  interface_list(filters : {mac_address: \"""" + mac + """\"}) {
    name
    ip_addresses {
      address
      custom_field_data
      nat_inside {
        address
      }
    }
    wireless_lans {
      id
      ssid
      auth_psk
      custom_field_data
    }
    device {
      services {
        name
        protocol
        ipaddresses {
          address
          custom_field_data
          nat_inside {
            address
          }
        }
        ports
        custom_field_data
      }
    }
  }
}"""
    return query

def create_query_ip(ip_id: int):
    """create a query string to get the ip address bearing a certain IP

    Args :
        id (int) : id of the ip"""
    
    query = """{
  ip_address(id: """+str(ip_id)+""") {
    address
  }
}"""
    return query
