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

import logging

log = logging.getLogger()

try:
    import  netmiko_multihop
except ImportError:
    log.info("cannot load netmiko_multihop, multihop ssh capability disabled")
    

from netmiko import ConnectHandler, SCPConn

from netmiko.exceptions import NetmikoAuthenticationException

import textfsmplus
import os
from jinjamator.plugins.content.fsm import process
from jinjamator.plugins.content.file import is_file


from netmiko import log as netmiko_log


def _get_missing_ssh_connection_vars():
    inject = []
    try:
        if not _jinjamator.configuration._data.get("ssh_username"):
            inject.append("ssh_username")
        if not _jinjamator.configuration._data.get("ssh_password"):
            inject.append("ssh_password")
        if not _jinjamator.configuration._data.get("ssh_host"):
            inject.append("ssh_host")
    except Exception as e:
        log.error(e)
        pass
    return inject

def process_ssh_opts(kwargs, defaults, prefix="ssh_", variables_to_parse=["host", "username", "password", "port", "device_type", "verbose"]):
    cfg = {}
    opts = {}
    for var_name in variables_to_parse:
        cfg[var_name] = kwargs.get(f"{prefix}{var_name}",
                        _jinjamator.configuration.get(f"{prefix}{var_name}", 
                        defaults.get(var_name)
                ),
        )
        try:
            del kwargs[prefix + var_name]
        except KeyError:
            pass
        try:
            del kwargs[var_name]
        except KeyError:
            pass
    # for var_name in kwargs:
    #     opts[var_name] = kwargs[var_name]
    return cfg,kwargs



def connect(*, _requires=_get_missing_ssh_connection_vars, **kwargs):
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

    jumphost_defaults = {
            'device_type': 'linux',
            'port': 22,
        }
 
    jumphost_cfg,opts = process_ssh_opts(kwargs,jumphost_defaults,"jumphost_")
    cfg,opts=process_ssh_opts(opts,defaults)

    if cfg["verbose"]:
        netmiko_log.setLevel(logging.DEBUG)
    else:
        netmiko_log.setLevel(logging.ERROR)


    if "jumphost_host" in kwargs:
        for var_name in ["username","password"]:
            if not jumphost_cfg[var_name]:
                #try to inherit username and password from target host
                jumphost_cfg[var_name]=cfg.get(var_name)
            jumphost_cfg["ip"]=jumphost_cfg["host"]
            del jumphost_cfg["host"]

            connection = ConnectHandler(**jumphost_cfg)
            
            cfg["ip"]=cfg["host"]
            del cfg["host"]
            

            connection.jump_to(**cfg)
            return connection

    else:
        try:
            cfg.update(opts)
            connection = ConnectHandler(**cfg)

            return connection
        except NetmikoAuthenticationException as e:
            if _jinjamator.configuration["best_effort"]:
                _jinjamator._log.error(
                    f'ssh {cfg["username"]}@{cfg["host"]}:{cfg["port"]}, login failed. Please check your credentials.'
                )
                return ""
            else:
                raise Exception(
                    f'ssh {cfg["username"]}@{cfg["host"]}:{cfg["port"]}, login failed. Please check your credentials.'
                )


def query(
    command, connection=None, *, _requires=_get_missing_ssh_connection_vars, **kwargs
):

    config = run(command, connection, **kwargs)
    cfg, opts=process_ssh_opts(kwargs,{},"jumphost_")
    cfg, opts=process_ssh_opts(opts,{},"ssh_")

    return process(cfg.get("device_type"), command, config)


def disconnect(connection):
    connection.cleanup()


def run(
    command, connection=None, *, _requires=_get_missing_ssh_connection_vars, **kwargs
):
    auto_disconnect = False
    if not connection:
        connection = connect(**kwargs)
        auto_disconnect = True

    cfg, opts=process_ssh_opts(kwargs,{},"jumphost_")
    cfg, opts=process_ssh_opts(opts,{},"ssh_")

    retval = connection.send_command_expect(
        command, read_timeout=kwargs.get("read_timeout", 300), **opts
    )
    if auto_disconnect:
        disconnect(connection)
    # netmiko_log.setLevel(backup_log_level)
    return retval


def run_mlt(
    commands, connection=None, *, _requires=_get_missing_ssh_connection_vars, **kwargs
):
    auto_disconnect = False
    if not connection:
        connection = connect(**kwargs)
        auto_disconnect = True

    cfg, opts=process_ssh_opts(kwargs,{},"jumphost_")
    cfg, opts=process_ssh_opts(opts,{},"ssh_")


    retval = connection.send_multiline_timing(commands, **opts)
    if auto_disconnect:
        disconnect(connection)
    # netmiko_log.setLevel(backup_log_level)
    return retval


def configure(
    commands_or_path,
    connection=None,
    *,
    _requires=_get_missing_ssh_connection_vars,
    **kwargs,
):
    auto_disconnect = False
    commands = commands_or_path
    if os.path.isfile(commands_or_path):
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

    cfg, opts=process_ssh_opts(kwargs,{},"jumphost_")
    cfg, opts=process_ssh_opts(opts,{},"ssh_")

    retval = connection.send_config_set(commands, **opts)

    if auto_disconnect:
        disconnect(connection)
    # netmiko_log.setLevel(backup_log_level)
    return retval


def get_file(
    src, dst, connection=None, *, _requires=_get_missing_ssh_connection_vars, **kwargs
):
    auto_disconnect = False
    if not connection:
        connection = connect(**kwargs)
        auto_disconnect = True

    cfg, opts=process_ssh_opts(kwargs,{},"jumphost_")
    cfg, opts=process_ssh_opts(opts,{},"ssh_")

    scp = SCPConn(connection)
    scp.scp_get_file(src, dst)
    # Needed
    scp.close()


def put_file(
    src, dst, connection=None, *, _requires=_get_missing_ssh_connection_vars, **kwargs
):
    auto_disconnect = False
    if not connection:
        connection = connect(**kwargs)
        auto_disconnect = True

    cfg, opts=process_ssh_opts(kwargs,{},"jumphost_")
    cfg, opts=process_ssh_opts(opts,{},"ssh_")

    scp = SCPConn(connection)
    scp.scp_put_file(src, dst)
    # Needed
    scp.close()
