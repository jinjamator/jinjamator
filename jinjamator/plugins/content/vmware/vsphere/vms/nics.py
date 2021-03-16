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

from pyVmomi import vim
import re
from jinjamator.plugins.content.mac import to_unix as mac_to_unix


def find(search=None, vm_name=None, content=None, attribute="mac_address"):
    retval = {}
    vms = vmware.vsphere.vms.find(vm_name)
    for vm in vms:
        val = vmware.vsphere.vm.nics.find(vm, search, attribute=attribute)
        if val:
            retval[vm.name] = val
    return retval
