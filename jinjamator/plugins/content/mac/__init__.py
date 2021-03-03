from netaddr import EUI, mac_unix_expanded


def to_unix(mac_address):
    mac = EUI(mac_address)
    mac.dialect = mac_unix_expanded
    return str(mac)


def to_aci(mac_address):
    return to_unix(mac_address)
