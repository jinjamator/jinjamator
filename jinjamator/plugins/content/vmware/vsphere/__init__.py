# Copyright 2021 Wilhelm Putz

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# based on https://github.com/vmware/pyvmomi-community-samples
#

from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim

vsphere_connection_pool = {}


def get_content(service_instance=None, cache=True):
    if cache:
        _cfg = _jinjamator.configuration
        if vsphere_connection_pool.get(_cfg["vsphere_host"]):
            if (
                vsphere_connection_pool[_cfg["vsphere_host"]]
                .get(_cfg["vsphere_username"], {})
                .get("content")
            ):
                log.debug("Using cached content")
                return (
                    vsphere_connection_pool[_cfg["vsphere_host"]]
                    .get(_cfg["vsphere_username"], {})
                    .get("content")
                )

    if not service_instance:
        service_instance = connect()
    content = service_instance.RetrieveContent()
    if cache:
        vsphere_connection_pool[_cfg["vsphere_host"]][_cfg["vsphere_username"]][
            "content"
        ] = content
    return content


def get_obj(vimtype, name, content=None):
    if not content:
        content = get_content()
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True
    )
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj


def connect(host=None, username=None, password=None, cache=True):
    _cfg = _jinjamator.configuration
    for param in ["vsphere_host", "vsphere_username", "vsphere_password"]:
        if locals().get(param):
            _cfg[param] = locals()[param]
        if not _cfg[param]:
            _jinjamator.handle_undefined_var(param)
    if cache:
        if vsphere_connection_pool.get(_cfg["vsphere_host"]):

            if vsphere_connection_pool[_cfg["vsphere_host"]].get(
                _cfg["vsphere_username"]
            ):
                log.debug(
                    f'Using cached connection to VSphere host {_cfg["vsphere_host"]}'
                )
                return vsphere_connection_pool[_cfg["vsphere_host"]][
                    _cfg["vsphere_username"]
                ]["service_instance"]

    service_instance = SmartConnectNoSSL(
        host=_cfg["vsphere_host"],
        user=_cfg["vsphere_username"],
        pwd=_cfg["vsphere_password"],
        port=443,
    )
    if service_instance:
        log.debug(f"Connected VSphere host {_cfg['vsphere_host']}")
    else:
        raise Exception(f"Cannot connect VSphere host {_cfg['vsphere_host']}")
    if cache:

        vsphere_connection_pool[_cfg["vsphere_host"]] = {
            _cfg["vsphere_username"]: {"service_instance": service_instance}
        }
    return service_instance
