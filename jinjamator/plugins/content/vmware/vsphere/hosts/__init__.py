from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import re


def list(service_instance_content=None):
    if not service_instance_content:
        service_instance_content = vmware.vsphere.get_content()
    log.debug("Getting all ESX hosts ...")
    host_view = service_instance_content.viewManager.CreateContainerView(
        service_instance_content.rootFolder, [vim.HostSystem], True
    )
    obj = [host for host in host_view.view]
    host_view.Destroy()
    return obj


def find(search, service_instance_content=None):
    rgx = re.compile(search)
    retval = []
    for host in list():
        if rgx.search(str(host)):
            retval.append(host)
    return retval
