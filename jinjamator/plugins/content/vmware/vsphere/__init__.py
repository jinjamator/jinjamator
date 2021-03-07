from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim


def get_content(service_instance=None):
    if not service_instance:
        service_instance = connect()
    return service_instance.RetrieveContent()


def connect(host=None, username=None, password=None):
    for param in ["vsphere_host", "vsphere_username", "vsphere_password"]:
        if locals().get(param):
            _jinjamator.configuration[param] = locals()[param]
        if not _jinjamator.configuration[param]:
            _jinjamator.handle_undefined_var(param)

    service_instance = SmartConnectNoSSL(
        host=_jinjamator.configuration["vsphere_host"],
        user=_jinjamator.configuration["vsphere_username"],
        pwd=_jinjamator.configuration["vsphere_password"],
        port=443,
    )
    if service_instance:
        log.debug(f"Connected VSphere host {_jinjamator.configuration['vsphere_host']}")
    else:
        raise Exception(
            f"Cannot connect VSphere host {_jinjamator.configuration['vsphere_host']}"
        )
    return service_instance
