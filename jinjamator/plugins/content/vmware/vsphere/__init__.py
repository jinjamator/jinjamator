from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim

vsphere_connection_pool = {}


def get_content(service_instance=None):
    if not service_instance:
        service_instance = connect()
    return service_instance.RetrieveContent()


def connect(host=None, username=None, password=None, cache=True):

    for param in ["vsphere_host", "vsphere_username", "vsphere_password"]:
        if locals().get(param):
            _jinjamator.configuration[param] = locals()[param]
        if not _jinjamator.configuration[param]:
            _jinjamator.handle_undefined_var(param)
    if cache:
        if vsphere_connection_pool.get(_jinjamator.configuration["vsphere_host"]):

            if vsphere_connection_pool[_jinjamator.configuration["vsphere_host"]].get(
                _jinjamator.configuration["vsphere_username"]
            ):
                log.debug(
                    f'Using cached connection to VSphere host {_jinjamator.configuration["vsphere_host"]}'
                )
                return vsphere_connection_pool[
                    _jinjamator.configuration["vsphere_host"]
                ][_jinjamator.configuration["vsphere_username"]]

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
    if cache:

        vsphere_connection_pool[_jinjamator.configuration["vsphere_host"]] = {
            _jinjamator.configuration["vsphere_username"]: service_instance
        }
    return service_instance
