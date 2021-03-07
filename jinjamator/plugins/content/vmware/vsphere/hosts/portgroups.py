import re


def list(hosts=None):
    if hosts == None:
        hosts = vmware.vsphere.hosts.list()
    retval = {}
    for host in hosts:
        pg = host.config.network.portgroup
        retval[host] = pg
    return retval


def find(search, return_type="obj", hosts=None):
    rgx = re.compile(search)
    retval = {}
    for host, obj in list(hosts).items():
        retval[host] = []
        for pg in obj:
            if rgx.search(str(pg.key)):
                log.debug(f"found portgroup key: {pg.key}")
                if return_type == "name":
                    retval[host].append(pg.key.replace("key-vim.host.PortGroup-", ""))
                elif return_type == "obj":
                    retval[host].append(pg)
                else:
                    retval[host].append(pg)
    return retval
