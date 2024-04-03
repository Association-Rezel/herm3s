"""
Definition of classes for the manipulation of network information
"""

from enum import Enum

class Protocol(Enum) :
    """Define the possible protocols for PAT rules in Netbox"""

    TCP = "tcp"
    UDP = "udp"

def str_to_protocol(s: str) -> Protocol :
    """Convert a string to a Protocol object
    
    Args :
        s (str) : string to convert to Protocol"""
    lowered_string = s.lower()
    if lowered_string == "tcp" :
        return Protocol.TCP
    elif lowered_string == "udp" :
        return Protocol.UDP
    else :
        raise ValueError(f"{s} is not a valid name for a protocol")
