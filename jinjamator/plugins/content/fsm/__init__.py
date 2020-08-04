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

import textfsm
import os

try:
    from textfsm import clitable
except ImportError:
    import clitable


def _clitable_to_dict(cli_table):
    """Convert TextFSM cli_table object to list of dictionaries."""
    objs = []
    for row in cli_table:
        temp_dict = {}
        for index, element in enumerate(row):
            temp_dict[cli_table.header[index].lower()] = element
        objs.append(temp_dict)

    return objs


def fsm_process(device_type=None, command=None, data=None):
    """Return the structured data based on the output from a network device."""

    cli_table = clitable.CliTable(
        "index", "{0}/fsmtemplates".format(os.path.dirname(os.path.abspath(__file__)))
    )

    attrs = dict(Command=command, Platform=device_type)
    cli_table.ParseCmd(data, attrs)
    structured_data = _clitable_to_dict(cli_table)
    return structured_data
