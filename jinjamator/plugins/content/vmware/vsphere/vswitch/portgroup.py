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


def create(
    vlan_id,
    portgroup_name=None,
    hosts=None,
    vswitch_name="vSwitch0",
    active_nics=[],
    standby_nics=[],
    promiscuous=False,
    mac_changes=False,
    forged_transmits=False,
):

    portgroup_spec = vim.host.PortGroup.Specification()
    portgroup_spec.vswitchName = vswitch_name
    if not portgroup_name:
        portgroup_name = f"VLAN{str(vlan_id).zfill(4)}"

    portgroup_spec.name = portgroup_name
    portgroup_spec.vlanId = int(vlan_id)
    network_policy = vim.host.NetworkPolicy()

    # set security
    network_policy.security = vim.host.NetworkPolicy.SecurityPolicy()
    network_policy.security.allowPromiscuous = promiscuous
    network_policy.security.macChanges = mac_changes
    network_policy.security.forgedTransmits = forged_transmits

    # set teaming
    if active_nics or standby_nics:
        network_policy.nicTeaming = vim.host.NetworkPolicy.NicTeamingPolicy()
        network_policy.nicTeaming.nicOrder = vim.host.NetworkPolicy.NicOrderPolicy()
        network_policy.nicTeaming.nicOrder.activeNic = active_nics
        network_policy.nicTeaming.nicOrder.standbyNic = standby_nics

    portgroup_spec.policy = network_policy

    if not hosts:
        hosts = vmware.vsphere.hosts.list()

    if not isinstance(hosts, list):
        hosts = [hosts]

    for host in hosts:
        try:
            host.configManager.networkSystem.AddPortGroup(portgroup_spec)
        except vim.fault.AlreadyExists:
            host.configManager.networkSystem.UpdatePortGroup(
                pgName=portgroup_name, portgrp=portgroup_spec
            )
