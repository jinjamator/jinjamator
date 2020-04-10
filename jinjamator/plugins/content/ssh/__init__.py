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

try:
    from textfsm import clitable
except ImportError:
    import clitable


def run(command, **kwargs):
    defaults = {
        "port": 22,
        "device_type": "cisco_nxos",
        "fast_cli": True,
        "verbose": False,
    }

    cfg = {}
    for var_name in ["host", "username", "password", "port", "device_type", "fast_cli"]:
        cfg[var_name] = (
            kwargs.get(var_name)
            or self._parent.configuration.get(f"ssh_{var_name}")
            or defaults.get(var_name)
            or self._parent.handle_undefined_var(f"ssh_{var_name}")
        )

    try:
        connection = ConnectHandler(**cfg)
    except ssh_exception.NetMikoAuthenticationException as e:
        if self._parent.configuration["best_effort"]:
            self._parent._log.error(
                f'Unable to run command {command} on platform {cfg["device_type"]} - {str(e)}'
            )
            return ""
        else:
            raise Exception(
                f'Unable to run command {command} on platform {cfg["device_type"]} - {str(e)}'
            )

    retval = connection.send_command_expect(command, max_loops=10000)
    connection.cleanup()
    return retval


def query(command, **kwargs):
    device_type = (
        kwargs.get("device_type")
        or self._parent.configuration.get(f"ssh_device_type")
        or "cisco_nxos"
    )
    kwargs["device_type"] = device_type
    config = run(command, **kwargs)

    return fsm_process(device_type, command, config)
