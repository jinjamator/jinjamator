fsm
===============================================

.. toctree::
    :maxdepth: 1



.. py:function:: fsm.process(device_type, command, data):

    Return the structured data based on the output from a device.
    For a complete list of currently supported devices and commands please refer to https://github.com/jinjamator/jinjamator/tree/master/jinjamator/plugins/content/fsm/fsmtemplates

    :param device_type: Platform from which the data was taken.
        Currently following platforms are supported:
            * alcatel_aos
            * alcatel_sros
            * arista_eos
            * aruba_os
            * avaya_ers
            * avaya_vsp
            * barracuda_fwng
            * brocade_fastiron
            * brocade_netiron
            * checkpoint_gaia
            * cisco_asa
            * cisco_ios
            * cisco_nxos
            * cisco_wlc
            * cisco_xr
            * dell_force10
            * hp_comware
            * hp_procurve
            * juniper_junos
            * juniper_screenos
            * paloalto_panos
            * ubiquiti_edgeswitch
            * vmware_nsxv
            * vyatta_vyos

    :type device_type: str
    :param command: The command from which the data was generated. Eg. show inventory, sh inv
    :type command: str
    :param data: Text which was produced by the command.
    :type data: str
    :return: A datastructure which contains the parsed data
    :rtype: list of dict
    
    


