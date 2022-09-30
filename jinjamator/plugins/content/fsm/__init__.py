# Copyright 2019 Wilhelm Putz

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

import textfsmplus
import os

try:
    from textfsmplus import clitable
except ImportError:
    import clitable

try:
    import ntc_templates

    ntc_templates_path = os.path.sep.join(
        [os.path.dirname(os.path.abspath(ntc_templates.__file__)), "templates"]
    )
except ImportError:
    ntc_templates_path = None


def _clitable_to_dict(cli_table):
    """Convert TextFSM cli_table object to list of dictionaries.

    :param cli_table:
    :type cli_table: textfsmplus CliTable object
    :return: a list of dict containing the data of the textfsmplus CliTable object.
    :rtype: list of dict
    """
    objs = []
    for row in cli_table:
        temp_dict = {}
        for index, element in enumerate(row):
            temp_dict[cli_table.header[index].lower()] = element
        objs.append(temp_dict)

    return objs


def process(device_type, command, data):
    """Return the structured data based on the output from a device.
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

    """

    # internal templates
    cli_table = clitable.CliTable(
        "index", "{0}/fsmtemplates".format(os.path.dirname(os.path.abspath(__file__)))
    )
    attrs = dict(Command=command, Platform=device_type)

    try:
        cli_table.ParseCmd(data, attrs)
    except textfsmplus.clitable.CliTableError:
        if ntc_templates_path:
            cli_table = clitable.CliTable("index", ntc_templates_path)
            cli_table.ParseCmd(data, attrs)

    structured_data = _clitable_to_dict(cli_table)
    return structured_data
