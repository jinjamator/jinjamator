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

import sys
import os

from jinjamator.tools.output_plugin_base import outputPluginBase
from pprint import pprint
import os
import json
import errno
import netmiko
import getpass
from netmiko.cisco_base_connection import CiscoBaseConnection
import re

from collections import defaultdict


def tree():
    return defaultdict(tree)


class SSHConfigurationError(Exception):
    pass


def send_config_set(
    self,
    config_commands=None,
    exit_config_mode=True,
    delay_factor=1,
    max_loops=150,
    strip_prompt=False,
    strip_command=False,
    config_mode_command=None,
    cmd_verify=True,
    enter_config_mode=True,
):
    """
        Send configuration commands down the SSH channel.
        config_commands is an iterable containing all of the configuration commands.
        The commands will be executed one after the other.
        Automatically exits/enters configuration mode.
        :param config_commands: Multiple configuration commands to be sent to the device
        :type config_commands: list or string
        :param exit_config_mode: Determines whether or not to exit config mode after complete
        :type exit_config_mode: bool
        :param delay_factor: Factor to adjust delays
        :type delay_factor: int
        :param max_loops: Controls wait time in conjunction with delay_factor (default: 150)
        :type max_loops: int
        :param strip_prompt: Determines whether or not to strip the prompt
        :type strip_prompt: bool
        :param strip_command: Determines whether or not to strip the command
        :type strip_command: bool
        :param config_mode_command: The command to enter into config mode
        :type config_mode_command: str
        :param cmd_verify: Whether or not to verify command echo for each command in config_set
        :type cmd_verify: bool
        :param enter_config_mode: Do you enter config mode before sending config commands
        :type exit_config_mode: bool
        """

    delay_factor = self.select_delay_factor(delay_factor)
    if config_commands is None:
        return ""
    elif isinstance(config_commands, str):
        config_commands = (config_commands,)

    if not hasattr(config_commands, "__iter__"):
        raise ValueError("Invalid argument passed into send_config_set")

    # Send config commands
    output = ""
    if enter_config_mode:
        cfg_mode_args = (config_mode_command,) if config_mode_command else tuple()
        output += self.config_mode(*cfg_mode_args)

    if self.fast_cli:
        for cmd in config_commands:
            self.write_channel(self.normalize_cmd(cmd))
        # Gather output
        output += self._read_channel_timing(
            delay_factor=delay_factor, max_loops=max_loops
        )
    elif not cmd_verify:
        for cmd in config_commands:
            self.write_channel(self.normalize_cmd(cmd))
            time.sleep(delay_factor * 0.05)
        # Gather output
        output += self._read_channel_timing(
            delay_factor=delay_factor, max_loops=max_loops
        )
    else:
        for cmd in config_commands:
            self.write_channel(self.normalize_cmd(cmd))

            # Make sure command is echoed
            new_output = self.read_until_pattern(pattern=re.escape(cmd.strip()))
            output += new_output

            # We might capture next prompt in the original read
            pattern = f"(?:{re.escape(self.base_prompt)}|#)"
            if not re.search(pattern, new_output):
                # Make sure trailing prompt comes back (after command)
                # NX-OS has fast-buffering problem where it immediately echoes command
                # Even though the device hasn't caught up with processing command.
                new_output = self.read_until_pattern(pattern=pattern)
                output += new_output
            if "Error:" in output:
                raise SSHConfigurationError(output)

    if exit_config_mode:
        output += self.exit_config_mode()
    output = self._sanitize_output(output)
    return output


CiscoBaseConnection.send_config_set = send_config_set


class ssh(outputPluginBase):
    def addArguments(self):
        self._parent._parser.add_argument(
            "-l",
            "--ssh-username",
            dest="ssh_username",
            help="username [default: %(default)s]",
        )
        self._parent._parser.add_argument(
            "-p", "--ssh-password", dest="ssh_password", help="password"
        )
        self._parent._parser.add_argument(
            "--ssh-device-type",
            dest="ssh_device_type",
            help="netmiko device_type [default: %(default)s]",
            default="cisco_nxos",
        )
        self._parent._parser.add_argument(
            "--ssh-port",
            dest="ssh_port",
            help="netmiko port [default: %(default)s]",
            default="22",
        )
        self._parent._parser.add_argument(
            "--ssh-hostname", dest="ssh_hostname", help="destination host"
        )

    def connect(self, **kwargs):
        self.init_plugin_params()

        pass

    def get_json_form(configuration={}):
        form = tree()
        form["schema"]["type"] = "object"

        form["schema"]["properties"]["ssh_device_type"]["title"] = "Netmiko Device Type"
        form["schema"]["properties"]["ssh_device_type"]["type"] = "string"
        form["schema"]["properties"]["ssh_device_type"][
            "description"
        ] = "Netmiko Device Type"
        form["schema"]["properties"]["ssh_device_type"]["enum"] = [
            "checkpoint_gaia",
            "paloalto_panos",
            "pluribus",
            "dell_force10",
            "dell_isilon",
            "dell_os10",
            "fortinet",
            "extreme_slx",
            "extreme_vsp",
            "extreme_nos",
            "extreme_ers",
            "extreme_wing",
            "a10",
            "netapp_cdot",
            "flexvnf",
            "mikrotik",
            "linux",
            "alcatel_sros",
            "alcatel_aos",
            "f5_tmsh",
            "f5_linux",
            "f5_ltm",
            "enterasys",
            "coriant",
            "vyos",
            "netscaler",
            "aruba",
            "cisco_xr",
            "cisco_nxos",
            "cisco_wlc",
            "cisco_asa",
            "quanta_mesh",
            "edge",
            "eltex",
            "ciena_saos",
            "mrv",
            "accedian",
            "ovs_linux",
            "brocade_nos",
            "huawei",
            "mellanox_mlnxos",
            "mellanox",
            "endace",
            "avaya_ers",
            "avaya_vsp",
        ]
        form["schema"]["properties"]["ssh_device_type"]["default"] = configuration.get(
            "ssh_device_type", "cisco_nxos"
        )

        form["schema"]["properties"]["ssh_port"]["title"] = "Port"
        form["schema"]["properties"]["ssh_port"]["type"] = "string"
        form["schema"]["properties"]["ssh_port"]["description"] = "SSH Port"
        form["schema"]["properties"]["ssh_port"]["default"] = configuration.get(
            "ssh_port", "22"
        )

        form["schema"]["properties"]["ssh_password"]["title"] = "Password"
        form["schema"]["properties"]["ssh_password"]["type"] = "string"
        form["schema"]["properties"]["ssh_password"]["description"] = "SSH password"
        form["schema"]["properties"]["ssh_password"]["format"] = "password"
        form["schema"]["properties"]["ssh_password"]["required"] = True
        form["schema"]["properties"]["ssh_password"]["default"] = configuration.get(
            "ssh_password", ""
        )

        form["schema"]["properties"]["ssh_username"]["title"] = "Username"
        form["schema"]["properties"]["ssh_username"]["type"] = "string"
        form["schema"]["properties"]["ssh_username"]["description"] = "SSH username"
        form["schema"]["properties"]["ssh_username"]["required"] = True
        form["schema"]["properties"]["ssh_username"]["default"] = configuration.get(
            "ssh_username", "admin"
        )

        form["schema"]["properties"]["ssh_hostname"]["title"] = "Hostname or IP"
        form["schema"]["properties"]["ssh_hostname"]["type"] = "string"
        form["schema"]["properties"]["ssh_hostname"][
            "description"
        ] = "Hostname or IP of the device where the task output will be applied"
        form["schema"]["properties"]["ssh_hostname"]["required"] = True
        form["schema"]["properties"]["ssh_hostname"]["default"] = configuration.get(
            "ssh_hostname", ""
        )

        form["options"]["fields"]["ssh_username"]["order"] = 1
        form["options"]["fields"]["ssh_password"]["order"] = 2
        form["options"]["fields"]["ssh_hostname"]["order"] = 3
        form["options"]["fields"]["ssh_device_type"]["order"] = 4
        form["options"]["fields"]["ssh_port"]["order"] = 5

        return dict(form)

    def init_plugin_params(self, **kwargs):

        self.ssh_hostname = self._parent.configuration.get(
            "ssh_hostname"
        ) or self._parent.handle_undefined_var("ssh_hostname")
        self.ssh_username = self._parent.configuration.get(
            "ssh_username"
        ) or self._parent.handle_undefined_var("ssh_username")
        self.ssh_password = self._parent.configuration.get(
            "ssh_password"
        ) or self._parent.handle_undefined_var("ssh_password")
        self.ssh_device_type = self._parent.configuration.get(
            "ssh_device_type"
        ) or self._parent.handle_undefined_var("ssh_device_type")
        self.ssh_port = self._parent.configuration.get(
            "ssh_port"
        ) or self._parent.handle_undefined_var("ssh_port")

    def process(self, data, **kwargs):

        conn = {
            "device_type": self.ssh_device_type,
            "ip": self.ssh_hostname,
            "username": self.ssh_username,
            "password": self.ssh_password,
            "port": self.ssh_port,
            "verbose": True,
            "fast_cli": False,
        }

        self._connection = netmiko.ConnectHandler(**conn)

        # self._connection.send_config_set = send_config_set

        retval = self._connection.send_config_set(data.split("\n"), delay_factor=0.0001)
        self._log.info("netmiko session information:\n{0}".format(retval))
        return retval
