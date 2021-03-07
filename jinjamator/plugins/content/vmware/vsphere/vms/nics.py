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

from pyVmomi import vim
import re
from jinjamator.plugins.content.mac import to_unix as mac_to_unix


def find(vm, search=None, content=None, attribute="mac_address"):
    if not content:
        content = vmware.vsphere.get_content()
    retval = {}
    for dev in vm.config.hardware.device:
        if isinstance(dev, vim.vm.device.VirtualEthernetCard):
            dev_backing = dev.backing
            port_group = None
            vlan_id = None
            vswitch = None
            if hasattr(dev_backing, "port"):
                portGroupKey = dev.backing.port.portgroupKey
                dvsUuid = dev.backing.port.switchUuid
                try:
                    dvs = content.dvSwitchManager.QueryDvsByUuid(dvsUuid)
                except:
                    port_group = "** Error: DVS not found **"
                    vlan_id = None
                    vswitch = None
                else:
                    pgObj = dvs.LookupDvPortGroup(portGroupKey)
                    port_group = pgObj.config.name
                    vlan_id = str(pgObj.config.defaultPortConfig.vlan.vlan_id)
                    vswitch = str(dvs.name)
            else:
                port_group = dev.backing.network.name
                vm_host = vm.runtime.host

                hosts = vmware.vsphere.hosts.list()
                host_pos = hosts.index(vm_host)
                viewHost = hosts[host_pos]

                pgs = vmware.vsphere.hosts.portgroups.list()[viewHost]
                for p in pgs:
                    if port_group in p.key:
                        vlan_id = str(p.spec.vlanId)
                        vswitch = str(p.spec.vswitchName)
            if search:
                if attribute == "mac_address":
                    if mac_to_unix(dev.macAddress) != mac_to_unix(search):
                        continue
                elif attribute == "vlan_id":
                    if int(vlan_id) != int(search):
                        continue
                else:
                    log.error(
                        f"VM NIC search for attribute {attribute} not yet implemented"
                    )
            retval[dev.deviceInfo.label] = {
                "mac_address": dev.macAddress,
                "vswitch": vswitch,
                "port_group": port_group,
                "vlan_id": vlan_id,
                "slot": dev.slotInfo.pciSlotNumber,
                "cdn_linux": f"ens{dev.slotInfo.pciSlotNumber}",
                "device": dev,
            }
    return retval


def list(vm, content=None):
    return find(vm, content=content)
