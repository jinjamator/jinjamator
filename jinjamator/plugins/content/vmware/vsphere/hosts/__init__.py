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

from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import re

host_cache = {}


def list(service_instance_content=None, cache=True):
    if not service_instance_content:
        service_instance_content = vmware.vsphere.get_content()
    if cache:
        if host_cache.get(id(service_instance_content)):
            log.debug("Using cached hosts")
            return host_cache.get(id(service_instance_content))

    log.debug("Getting all ESX hosts ...")
    host_view = service_instance_content.viewManager.CreateContainerView(
        service_instance_content.rootFolder, [vim.HostSystem], True
    )
    obj = [host for host in host_view.view]
    if cache:
        host_cache[id(service_instance_content)] = obj
    host_view.Destroy()
    return obj


def find(search, service_instance_content=None):
    rgx = re.compile(search)
    retval = []
    for host in list():
        if rgx.search(str(host)):
            retval.append(host)
    return retval
