def ensure_portgroup_exists(
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
        hosts = vmware.vsphere.connect()

    if not isinstance(hosts, list):
        hosts = [hosts]

    for host in hosts:
        try:
            host.configManager.networkSystem.AddPortGroup(portgroup_spec)
        except vim.fault.AlreadyExists:
            host.configManager.networkSystem.UpdatePortGroup(
                pgName=portgroup_name, portgrp=portgroup_spec
            )
