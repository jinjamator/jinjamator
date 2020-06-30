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

from netmiko import ConnectHandler, ssh_exception
import textfsm
import os
from jinjamator.plugins.content.fsm import fsm_process
import logging

log = logging.getLogger()
from netmiko import log as netmiko_log

try:
    from textfsm import clitable
except ImportError:
    import clitable


def run(command, **kwargs):
    defaults = {
        "port": 22,
        "device_type": "cisco_nxos",
        "fast_cli": False,
        "verbose": False,
    }

    cfg = {}
    opts = {}
    for var_name in ["host", "username", "password", "port", "device_type"]:
        cfg[var_name] = (
            kwargs.get(var_name)
            or _jinjamator.configuration.get(f"ssh_{var_name}")
            or defaults.get(var_name)
            or _jinjamator.handle_undefined_var(f"ssh_{var_name}")
        )
        try:
            del kwargs[var_name]
        except KeyError:
            pass
    for var_name in kwargs:
        opts[var_name] = kwargs[var_name]

    try:
        backup_log_level = log.level
        netmiko_log.setLevel(logging.INFO)
        connection = ConnectHandler(**cfg)
    except ssh_exception.NetMikoAuthenticationException as e:
        netmiko_log.setLevel(backup_log_level)
        if _jinjamator.configuration["best_effort"]:
            _jinjamator._log.error(
                f'Unable to run command {command} on platform {cfg["device_type"]} - {str(e)}'
            )
            return ""
        else:
            raise Exception(
                f'Unable to run command {command} on platform {cfg["device_type"]} - {str(e)}'
            )

    retval = connection.send_command_expect(command, max_loops=10000, **opts)
    connection.cleanup()
    netmiko_log.setLevel(backup_log_level)
    return retval


def query(command, **kwargs):
    device_type = (
        kwargs.get("device_type")
        or _jinjamator.configuration.get(f"ssh_device_type")
        or _jinjamator.handle_undefined_var("ssh_device_type")
    )
    kwargs["device_type"] = device_type
    config = run(command, **kwargs)

    return fsm_process(device_type, command, config)
