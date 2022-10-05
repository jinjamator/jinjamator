import jinja2
import ipcalc


def subnet_mask(prefix):
    sn = ipcalc.Network(prefix)
    return sn.netmask()


def length(prefix):
    sn = ipcalc.Network(prefix)
    return sn.subnet()


def subnet(prefix):
    sn = ipcalc.Network(prefix)
    return sn.subnet()


def ip(prefix):
    return prefix.split("/")[0]


def gateway(prefix):

    return ipcalc.Network(prefix).host_first()

def network (prefix):
    sn = ipcalc.Network(prefix)
    return sn.network()