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

from netmiko import ConnectHandler, SCPConn
from netmiko.exceptions import NetmikoAuthenticationException

import textfsmplus
import os
from jinjamator.plugins.content.fsm import process
from jinjamator.plugins.content.file import is_file

import logging

log = logging.getLogger()
from netmiko import log as netmiko_log

try:
    from textfsmplus import clitable
except ImportError:
    import clitable


def connect(**kwargs):
    """Run a command via SSH and return the text output.

    :param command: The command that should be run.
    :type command: ``str``
    :raises Exception: If the command cannot be run on the remote device and best_effort is not set within the task.
    :return: The text output of the command.
    :rtype: ``str``

    :Keyword Arguments:
        * *ssh_username* (``str``), ``optional``, ``jinjamator enforced`` --
           Username for the SSH connection. If not set in task configuration or via keyword argument jinjamator asks the user to input the data.
        * *ssh_password* (``str``), ``optional``, ``jinjamator enforced`` --
           Password for the SSH connection. If not set in task configuration or via keyword argument jinjamator asks the user to input the data.
        * *ssh_host*  (``str``), ``optional``, ``jinjamator enforced`` --
           Target hostname or IP address for the SSH connection. If not set in task configuration or via keyword argument jinjamator asks the user to input the data.
        * *ssh_port* (``int``), ``optional`` --
           SSH TCP port, defaults to 22
        * *ssh_device_type* (``str``), ``optional`` --
           Netmiko device type, defaults to "cisco_nxos". 
           Currently supported device_types can be found here: https://github.com/ktbyers/netmiko/tree/develop/netmiko 
        * *fast_cli* (``bool``), ``optional`` --
           Use Netmiko fast_cli mode, defaults to False
        * *verbose* (``bool``), ``optional`` --
           Set Netmiko to debug mode, defaults to False

    :Examples:
        If one of the following conditions are met,
            * *ssh_username*, *ssh_password*, *ssh_host* is specified via command line parameter in CLI Mode e.g -m 'ssh_username':'admin'
            * Any of *ssh_username*, *ssh_password*, *ssh_host* is not specified via command line parameter in CLI Mode and the user enters the data correctly via CLI.
            * The task is run via Daemon mode and ssh_username, ssh_password, ssh_host are defined in the task defaults.yaml, environment site defaults.yaml.
            * The task is run via Daemon mode and ssh_username, ssh_password, ssh_host are entered correctly in the generated webform.
            
        
        the raw output of the command show inventory from a cisco nxos box is returned by the tasklet .

        jinja2 tasklet:
        
            .. code-block:: jinja
                
                {{ssh.run('show inventory')}} 

        python tasklet:

            .. code-block:: python

                return ssh.run('show inventory')

        To set the arguments directly on call of the function. The example will ask for the password and connects to 1.2.3.4 port 22 and runs the command "show inventory"

        jinja2 tasklet:
        
            .. code-block:: jinja
                
                {{ssh.run('show inventory',ssh_username=admin,ssh_host='1.2.3.4')}} 

        python tasklet:

            .. code-block:: python

                return ssh.run('show inventory',ssh_username='admin','ssh_host'='1.2.3.4')


    """

    defaults = {
        "port": 22,
        "device_type": "cisco_nxos",
        "fast_cli": False,
        "verbose": False,
    }

    cfg = {}
    opts = {}
    for var_name in ["host", "username", "password", "port", "device_type", "verbose"]:
        cfg[var_name] = kwargs.get(
            f"ssh_{var_name}",
            kwargs.get(
                var_name,
                _jinjamator.configuration.get(
                    f"ssh_{var_name}", defaults.get(var_name)
                ),
            ),
        )
        if cfg[var_name] == None:
            cfg[var_name] = _jinjamator.handle_undefined_var(f"ssh_{var_name}")
        try:
            del kwargs[var_name]
        except KeyError:
            pass
    for var_name in kwargs:
        opts[var_name] = kwargs[var_name]

    try:

        if cfg["verbose"]:
            netmiko_log.setLevel(logging.DEBUG)
        else:
            netmiko_log.setLevel(logging.ERROR)

        connection = ConnectHandler(**cfg,**opts)
        return connection
    except NetmikoAuthenticationException as e:

        if _jinjamator.configuration["best_effort"]:
            _jinjamator._log.error(
                f'Unable to run command {command} on platform {cfg["device_type"]} - {str(e)}'
            )
            return ""
        else:
            raise Exception(
                f'Unable to run command {command} on platform {cfg["device_type"]} - {str(e)}'
            )


def query(command, connection=None, **kwargs):
    device_type = (
        kwargs.get("device_type")
        or _jinjamator.configuration.get(f"ssh_device_type")
        or _jinjamator.handle_undefined_var("ssh_device_type")
    )
    kwargs["device_type"] = device_type

    config = run(command, connection, **kwargs)

    return process(device_type, command, config)


def disconnect(connection):
    connection.cleanup()


def run(command, connection=None, **kwargs):
    auto_disconnect = False
    if not connection:
        connection = connect(**kwargs)
        auto_disconnect = True

    opts = {}
    for var_name in ["host", "username", "password", "port", "device_type"]:
        try:
            del kwargs[var_name]
        except KeyError:
            pass
    for var_name in kwargs:
        opts[var_name] = kwargs[var_name]
    retval = connection.send_command_expect(command, read_timeout=300, **opts)
    if auto_disconnect:
        disconnect(connection)
    # netmiko_log.setLevel(backup_log_level)
    return retval

def run_mlt(commands,connection=None,**kwargs):
    auto_disconnect = False
    if not connection:
        connection = connect(**kwargs)
        auto_disconnect = True

    opts = {}
    for var_name in ["host", "username", "password", "port", "device_type"]:
        try:
            del kwargs[var_name]
        except KeyError:
            pass
    for var_name in kwargs:
        opts[var_name] = kwargs[var_name]
    retval = connection.send_multiline_timing(commands, **opts)
    if auto_disconnect:
        disconnect(connection)
    # netmiko_log.setLevel(backup_log_level)
    return retval

def configure(commands_or_path, connection=None, **kwargs):
    auto_disconnect = False
    commands = commands_or_path
    if is_file(commands_or_path):
        log.debug(f"loaded configuration from file {commands_or_path}")
        commands = [
            line.replace("\r", "") for line in file.load(commands_or_path).split("\n")
        ]
    elif isinstance(commands_or_path, str):
        log.debug(f"splitting configuration string into list {commands_or_path}")
        commands = [line.replace("\r", "") for line in commands_or_path.split("\n")]

    if not connection:
        connection = connect(**kwargs)
        auto_disconnect = True

    opts = {}
    for var_name in ["host", "username", "password", "port", "device_type"]:
        try:
            del kwargs[var_name]
        except KeyError:
            pass
    for var_name in kwargs:
        opts[var_name] = kwargs[var_name]

    retval = connection.send_config_set(commands, **opts)

    if auto_disconnect:
        disconnect(connection)
    # netmiko_log.setLevel(backup_log_level)
    return retval


def get_file (src,dst,connection=None,**kwargs):
    auto_disconnect = False
    if not connection:
        connection = connect(**kwargs)
        auto_disconnect = True

    opts = {}
    for var_name in ["host", "username", "password", "port", "device_type"]:
        try:
            del kwargs[var_name]
        except KeyError:
            pass
    for var_name in kwargs:
        opts[var_name] = kwargs[var_name]
    
    scp = SCPConn(connection)
    scp.scp_get_file(src,dst)
    #Needed
    scp.close()


def put_file (src,dst,connection=None,**kwargs):
    auto_disconnect = False
    if not connection:
        connection = connect(**kwargs)
        auto_disconnect = True

    opts = {}
    for var_name in ["host", "username", "password", "port", "device_type"]:
        try:
            del kwargs[var_name]
        except KeyError:
            pass
    for var_name in kwargs:
        opts[var_name] = kwargs[var_name]
    
    scp = SCPConn(connection)
    scp.scp_put_file(src,dst)
    #Needed
    scp.close()