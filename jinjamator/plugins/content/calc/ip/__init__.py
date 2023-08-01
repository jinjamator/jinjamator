import ipcalc
import re

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
    Returns the network of an IP-address
    Technically the return value is a ``ipcalc.IP`` object

    >>> print(network("192.168.0.5/24"))
    192.168.0.0

    :param ip: IP-address in CIDR-notation
    :type ip: string
    :returns: ipcalc.IP object
    :rtype: object
    """
    net = ipcalc.Network(ip)
    return net.network()

def network_cidr (ip):
    """
    Returns the network of an IP-address in CIDR notation
    Technically the return value is a ``ipcalc.IP`` object

    >>> print(network_cidr("192.168.0.5/24"))
    192.168.0.0/24

    :param ip: IP-address in CIDR-notation
    :type ip: string
    :returns: Network in CIDR notation
    :rtype: string
    """
    net = ipcalc.Network(ip)
    return str(net.network()) + "/" + str(net.subnet())





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
    Returns the IP-address part of a network given in CIDR-notation

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


def host_first (subnet):
    """
    Returns the first host of a network given in CIDR-notation

    >>> print(host_first("192.168.0.0/24"))
    192.168.0.1

    :param subnet: network in CIDR-notation
    :type subnet: string
    :returns: first host in network
    :rtype: string
    """
    net = ipcalc.Network(subnet)
    return net.host_first()

def host_last (subnet):
    """
    Returns the last host of a network given in CIDR-notation

    >>> print(host_last("192.168.0.0/24"))
    192.168.0.254

    :param subnet: network in CIDR-notation
    :type subnet: string
    :returns: last host in network
    :rtype: string
    """
    net = ipcalc.Network(subnet)
    return net.host_last()

def list_ips (subnet):
    """
    Lists all useable IPs of a network given in CIDR-notation
    Will assume /32 if no CIDR is given
    >>> print(list_ips("192.168.0.0/29"))
    ['192.168.0.1', '192.168.0.2', '192.168.0.3', '192.168.0.4', '192.168.0.5', '192.168.0.6']
    :param subnet: network in CIDR-notation
    :type subnet: string
    :returns: List of all useable IPs
    :rtype: list
    """

    ips = []
    for ip in ipcalc.Network(subnet):
        ips.append(str(ip))

    return ips


def expand_range (string):
    """
    Will return all IP's or ranges within the defined ranges
    >>> print(list_ips("192.168.0-3.0/29"))
    ['192.168.0.0/29', '192.168.1.0/29', '192.168.2.0/29', '192.168.3.0/29']
    >>> print(list_ips("192.168-169.0-2.5"))
    ['192.168.0.5', '192.168.1.5', '192.168.2.5', '192.169.0.5', '192.169.1.5', '192.169.2.5']
    :param subnet: network in CIDR-notation
    :type subnet: string
    :returns: List of all subnets/IPs that are in the defined range
    :rtype: list
    """

    #Return a list of the string even if not - can be found
    if not "-" in str(string): return [str(string)]

    #wrap between two dots
    string = "."+string+"."
    groups = re.match(r"(.*)\.(\d+-\d+)\.(.*)",string).groups()
    #print(groups)
    #('.100.76', '11-12', '.1')
    rparts = groups[1].split("-")
    ranges = []
    for i in range(int(rparts[0]),int(rparts[1])+1):
        rstr = f"{groups[0]}.{i}.{groups[2]}"
        #Remove the dots we added
        if rstr.startswith("."): rstr = rstr[1:]
        if rstr.endswith("."): rstr = rstr[:len(rstr)-1]

        if "-" in rstr:
            rranges = expand_range(rstr)
            if isinstance(rranges,list): ranges += rranges
            else:
                log.warning(f"Cannot add elements to range. Expected list, got {type(rranges)}: {rranges}")
        else:
            ranges.append(rstr)

    ranges.sort()
    return ranges