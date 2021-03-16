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


def list(content=None):
    if not content:
        content = vmware.vsphere.get_content()
    vm_view = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.VirtualMachine], True
    )
    obj = [vm for vm in vm_view.view]
    vm_view.Destroy()
    return obj


def list_names(content=None):
    return [vm.name for vm in list(content)]


def find(search, return_type="obj", service_instance_content=None):
    if not search:
        return list()
    rgx = re.compile(search)
    retval = []
    for obj in list():
        if rgx.search(str(obj.name)):
            if return_type == "name":
                retval.append(obj.name)
            elif return_type == "obj":
                retval.append(obj)
            else:
                retval.append(obj)
    return retval
