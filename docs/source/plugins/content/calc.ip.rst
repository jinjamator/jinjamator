calc.ip
===============================================

.. toctree::
    :maxdepth: 1

    calc.ip.prefix.rst


.. py:function:: calc.ip.expand_range(string):

    Will return all IP's or ranges within the defined ranges

    >>> print(expand_range("192.168.0-3.0/29"))
    ['192.168.0.0/29', '192.168.1.0/29', '192.168.2.0/29', '192.168.3.0/29']

    >>> print(expand_range("192.168-169.0-2.5"))
    ['192.168.0.5', '192.168.1.5', '192.168.2.5', '192.169.0.5', '192.169.1.5', '192.169.2.5']
    :param subnet: network in CIDR-notation
    :type subnet: string
    :returns: List of all subnets/IPs that are in the defined range
    :rtype: list
    

.. py:function:: calc.ip.host_first(subnet):

    Returns the first host of a network given in CIDR-notation

    >>> print(host_first("192.168.0.0/24"))
    192.168.0.1

    :param subnet: network in CIDR-notation
    :type subnet: string
    :returns: first host in network
    :rtype: string
    

.. py:function:: calc.ip.host_last(subnet):

    Returns the last host of a network given in CIDR-notation

    >>> print(host_last("192.168.0.0/24"))
    192.168.0.254

    :param subnet: network in CIDR-notation
    :type subnet: string
    :returns: last host in network
    :rtype: string
    

.. py:function:: calc.ip.ip(ip):

    Returns the IP-address part of a network given in CIDR-notation

    >>> print(ip("192.168.0.5/24"))
    192.168.0.5

    :param ip: IP-address/network in CIDR-notation
    :type ip: string
    :returns: IP-address without prefix-length
    :rtype: string
    

.. py:function:: calc.ip.is_in(ip, subnet):

    Check if ``ip`` is within ``subnet``
    >>> is_in("192.168.0.5","192.168.0.0/24")
    True

    :param ip: IP-address or network in CIDR-notation
    :type ip: string
    :param subnet: network in CIDR-notation
    :type subnet: string
    :returns: True or False
    :rtype: bool
    

.. py:function:: calc.ip.is_in_list(ip, subnet_list):

    Check if ``ip`` is within ``list of subnets``
    >>> is_in("192.168.0.5","[172.16.0.0/24, 192.168.0.0/24]")
    True

    :param ip: IP-address or network in CIDR-notation
    :type ip: string
    :param subnet_list: list of networks in CIDR-notation
    :type subnet_list: list
    :returns: True or False
    :rtype: bool
    

.. py:function:: calc.ip.is_ip(ip):

    Check if ``ip`` is an ip address
    >>> is_ip("192.168.0.5")
    True

    :param ip: IP-address that should be checked
    :type ip: string
    :returns: True or False
    :rtype: bool
    

.. py:function:: calc.ip.is_subnet(subnet):

    Check if ``subnet`` is a subnet.
    Also returns True if it is a host within a subnet
    >>> is_subnet("192.168.0.5/24")
    True

    :param subnet: Subnet in CIDR notation that should be checked
    :type subnet: string
    :returns: True or False
    :rtype: bool
    

.. py:function:: calc.ip.list_ips(subnet):

    Lists all useable IPs of a network given in CIDR-notation
    Will assume /32 if no CIDR is given
    >>> print(list_ips("192.168.0.0/29"))
    ['192.168.0.1', '192.168.0.2', '192.168.0.3', '192.168.0.4', '192.168.0.5', '192.168.0.6']
    :param subnet: network in CIDR-notation
    :type subnet: string
    :returns: List of all useable IPs
    :rtype: list
    

.. py:function:: calc.ip.netmask(ip):

    Returns the netmask of an IP-address/network in CIDR-notation
    Technically the return value is a ``ipcalc.IP`` object

    >>> print(netmask("192.168.0.0/24"))
    255.255.255.0

    :param ip: IP-address/network in CIDR-notation
    :type ip: string
    :returns: ipcalc.IP object
    :rtype: object
    

.. py:function:: calc.ip.netmask_to_cidr(netmask):

    Converts a netmask to a prefix used for CIDR-notation

    >>> print(netmask_to_cidr("255.255.255.0"))
    24

    :param netmask: Subnet-mask
    :type netmask: string
    :returns: prefix-length
    :rtype: integer
    

.. py:function:: calc.ip.netmask_to_wildcard(netmask):

    Converts a Subnetmask to its widely beloved wildcard equivalent

    >>> print(netmask_to_wildcard("255.255.255.0"))
    0.0.0.255

    :param netmask: Subnet-mask
    :type netmask: string
    :returns: Wildcasrd-mask
    :rtype: string
    

.. py:function:: calc.ip.network(ip):

    Returns the network of an IP-address
    Technically the return value is a ``ipcalc.IP`` object

    >>> print(network("192.168.0.5/24"))
    192.168.0.0

    :param ip: IP-address in CIDR-notation
    :type ip: string
    :returns: ipcalc.IP object
    :rtype: object
    

.. py:function:: calc.ip.network_cidr(ip):

    Returns the network of an IP-address in CIDR notation
    Technically the return value is a ``ipcalc.IP`` object

    >>> print(network_cidr("192.168.0.5/24"))
    192.168.0.0/24

    :param ip: IP-address in CIDR-notation
    :type ip: string
    :returns: Network in CIDR notation
    :rtype: string
    

.. py:function:: calc.ip.overlap(subnet1, subnet2):

    Check if ``subnet1`` and ``subnet2`` overlap
    >>> is_in("192.168.0.32/28","192.168.0.0/24")
    True

    :param subnet1: network in CIDR-notation
    :type subnet1: string
    :param subnet: network in CIDR-notation
    :type subnet: string
    :returns: True or False
    :rtype: bool
    

.. py:function:: calc.ip.prefix_len(ip):

    Returns the prefix-length part of a network given in CIDR-notation

    >>> print(prefix_len("192.168.0.5/24"))
    24

    :param ip: IP-address/network in CIDR-notation
    :type ip: string
    :returns: prefix-length
    :rtype: integer
    

.. py:function:: calc.ip.subnet(ip):

    Returns the prefix-length part of a network given in CIDR-notation

    >>> print(prefix_len("192.168.0.5/24"))
    24

    :param ip: IP-address/network in CIDR-notation
    :type ip: string
    :returns: prefix-length
    :rtype: integer
    


