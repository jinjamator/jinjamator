def dscp_map():
    """
    Internal function that returns a dict with valid DSCP names to thier decimal values

    :return: Dictionary containing the values (name => dec)
    :rtype: ``dict``
    """

    return {
        "CS0": 0,
        "CS1": 8,
        "CS2": 16,
        "CS3": 24,
        "CS4": 32,
        "CS5": 40,
        "CS6": 48,
        "CS7": 56,
        "AF11": 10,
        "AF12": 12,
        "AF13": 14,
        "AF21": 18,
        "AF22": 20,
        "AF23": 22,
        "AF31": 26,
        "AF32": 28,
        "AF33": 30,
        "AF41": 34,
        "AF42": 36,
        "AF43": 38,
        "EF": 46,
        "VOICE-ADMIT": 44  
    }

def name_to_dec (name):
    """
    Converts the DSCP name to it'S corresponding decimal value

    :param name: DSCP name (i.e. CS3)
    :type name: ``string``
    :return: Decimal DSCP value (i.e. 24). Returns False if no mapping could be found
    :rtype: ``int``
    """
    dscp = dscp_map()
    if name in dscp: return int(dscp[name])
    else: return False

def dec_to_name (dec):
    """
    Converts the DSCP decimal value to it'S corresponding name

    :param name: Decimal DSCP value (i.e. 24)
    :type name: ``int``
    :return: DSCP name (i.e. CS3). Returns False if no mapping could be found
    :rtype: ``str`` | ``bool``
    """
    dscp = dscp_map()
    for name,d in dscp.items():
        if d == dec: return name
    
    return False