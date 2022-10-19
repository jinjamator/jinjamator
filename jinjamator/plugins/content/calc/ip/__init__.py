import ipcalc

def is_in (ip,subnet):
    """
    Check if ``ip`` is within ``subnet``
    >>> is_in("192.168.0.5","192.168.0.0/24")
    True

    :param ip: IP-address or network in CIDR-notation
    :type ip: string
    :param subnet: network in CIDR-notation
    :type subnet: string
    :returns: True or False
    :rtype: bool
    """
    net = ipcalc.Network(subnet)
    return net.has_key(ip)


def overlap (subnet1,subnet2):
    """
    Check if ``subnet1`` and ``subnet2`` overlap
    >>> is_in("192.168.0.32/28","192.168.0.0/24")
    True

    :param subnet1: network in CIDR-notation
    :type subnet1: string
    :param subnet: network in CIDR-notation
    :type subnet: string
    :returns: True or False
    :rtype: bool
    """
    net = ipcalc.Network(subnet2)
    return net.has_key(subnet1)


def network (ip):
    """
    Returns the network of an IP-address in CIDR-notation
    Technically the return value is a ``ipcalc.IP`` object

    >>> print(network("192.168.0.5/24"))
    192.168.0.0/24

    :param ip: IP-address in CIDR-notation
    :type ip: string
    :returns: ipcalc.IP object
    :rtype: object
    """
    net = ipcalc.Network(ip)
    return net.network()


def netmask (ip):
    """
    Returns the netmask of an IP-address/network in CIDR-notation
    Technically the return value is a ``ipcalc.IP`` object

    >>> print(netmask("192.168.0.0/24"))
    255.255.255.0

    :param ip: IP-address/network in CIDR-notation
    :type ip: string
    :returns: ipcalc.IP object
    :rtype: object
    """
    net = ipcalc.Network(ip)
    return net.netmask()


def ip (ip):
    """
    Returns the IP-address/network part of a network given in CIDR-notation

    >>> print(ip("192.168.0.5/24"))
    192.168.0.5

    :param ip: IP-address/network in CIDR-notation
    :type ip: string
    :returns: IP-address without prefix-length
    :rtype: string
    """
    return ip.split("/")[0]


def prefix_len (ip):
    """
    Returns the prefix-length part of a network given in CIDR-notation

    >>> print(prefix_len("192.168.0.5/24"))
    24

    :param ip: IP-address/network in CIDR-notation
    :type ip: string
    :returns: prefix-length
    :rtype: integer
    """
    return int(ip.split("/")[1])


def subnet (ip):
    """
    Returns the prefix-length part of a network given in CIDR-notation

    >>> print(prefix_len("192.168.0.5/24"))
    24

    :param ip: IP-address/network in CIDR-notation
    :type ip: string
    :returns: prefix-length
    :rtype: integer
    """
    net = ipcalc.Network(ip)
    return net.subnet()


def netmask_to_cidr (netmask):
    """
    Converts a netmask to a prefix used for CIDR-notation

    >>> print(netmask_to_cidr("255.255.255.0"))
    24

    :param netmask: Subnet-mask
    :type netmask: string
    :returns: prefix-length
    :rtype: integer
    """
    bits = 0
    for part in str(netmask).split("."):
        bits += bin(int(part)).count("1")
    return int(bits)


def netmask_to_wildcard (netmask):
    """
    Converts a Subnetmask to its widely beloved wildcard equivalent

    >>> print(netmask_to_wildcard("255.255.255.0"))
    0.0.0.255

    :param netmask: Subnet-mask
    :type netmask: string
    :returns: Wildcasrd-mask
    :rtype: string
    """
    parts = []
    for part in str(netmask).split("."):
        parts.append(str(255-int(part)))
    return ".".join(parts)




