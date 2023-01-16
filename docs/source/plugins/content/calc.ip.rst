calc.ip
===============================================

.. toctree::
    :maxdepth: 1

    calc.ip.prefix.rst


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

    Returns the network of an IP-address in CIDR-notation
    Technically the return value is a ``ipcalc.IP`` object

    >>> print(network("192.168.0.5/24"))
    192.168.0.0/24

    :param ip: IP-address in CIDR-notation
    :type ip: string
    :returns: ipcalc.IP object
    :rtype: object
    

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
    


