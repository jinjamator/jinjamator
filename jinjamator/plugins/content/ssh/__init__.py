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
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
import xxhash
import copy

log = logging.getLogger()

try:
    import netmiko_multihop
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
    if _jinjamator.configuration._data.get("ssh_credentials"):
        # if we have ssh_credentials set we do not inject dependencies
        return inject
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


def process_ssh_opts(
    kwargs,
    defaults,
    prefix="ssh_",
    variables_to_parse=[
        "host",
        "username",
        "password",
        "port",
        "device_type",
        "verbose",
        "secret",
        "timeout",
        "session_log",
    ],
):
    cfg = {}
    opts = {}
    try:
        del kwargs["ssh_credentials"]
    except KeyError:
        pass
    try:
        del kwargs["ssh_max_concurrency"]
    except KeyError:
        pass

    for var_name in variables_to_parse:
        cfg[var_name] = kwargs.get(
            f"{prefix}{var_name}",
            _jinjamator.configuration.get(
                f"{prefix}{var_name}", defaults.get(var_name)
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
    return cfg, kwargs


def _mplexed_connect(*args, **kwargs):
    try:
        _con = _connect(*args, **kwargs)
        return _con
    except Exception as e:
        log.info(e)
        log.info(
            f'cannot connect using {kwargs.get("ssh_device_type")} {kwargs.get("ssh_username")}@{kwargs.get("ssh_host")}, skipping this variant'
        )
    try:
        disconnect(_con)
    except:
        pass

    return None


def _get_cache_id(ip,cred):
    relevant_vars = ["device_type","username","password","secret"]
    str_to_hash=ip.strip().lower()
    #derive hash seed from jinjamator app secret key.
    seed=int.from_bytes(_jinjamator._configuration["secret-key"].encode(), 'little')

    for var in relevant_vars:
        str_to_hash+=str(cred.get(var))

    return xxhash.xxh64('xxhash', seed=seed).hexdigest()

def _get_cache_dir():
    return  _jinjamator._configuration["jinjamator_user_directory"] + os.path.sep + "cache" + os.path.sep + "ssh_credentials"


def _save_as_last_working_cred_hash(ip,cred):
    cache_entry_id=_get_cache_id(ip,cred)
    cache_entry_path=_get_cache_dir() + os.path.sep + str(ip).strip().lower() 
    with open(cache_entry_path,"w") as fh:
        fh.write(cache_entry_id)

def _get_last_working_cred_hash(ip):
    cache_entry_path=_get_cache_dir() + os.path.sep + str(ip).strip().lower() 
    try:
        with open(cache_entry_path,"r") as fh:
            data=fh.read()
    except Exception:
        return "no entry found"
    return data



def ssh_credential_sort(_kwargs, var_prefix="ssh_"):
    cache_base_dir = _jinjamator._configuration["jinjamator_user_directory"] + os.path.sep + "cache" + os.path.sep + "ssh_credentials"
    os.makedirs(cache_base_dir, exist_ok=True)
    retval=[]
    ip=_kwargs.get("ssh_host").strip().lower()
    look_for=_get_last_working_cred_hash(ip)
    for cred in _kwargs.get("ssh_credentials"):
        _cred, opts = process_ssh_opts(copy.deepcopy(cred), {}, "ssh_")
        if _get_cache_id(ip, _cred) == look_for:
            retval.insert(0,cred)
        else:
            retval.append(cred)
    return retval

def connect(*args, _requires=_get_missing_ssh_connection_vars, **kwargs):
    if "ssh_credentials" in kwargs:
        for cred in ssh_credential_sort(kwargs):
            _kwargs = deepcopy(kwargs)
            _kwargs.update(cred)
            del _kwargs["ssh_credentials"]
            res = _mplexed_connect(*args, **_kwargs)
            if res:
                log.debug(
                    f'sucessfully connected {kwargs.get("ssh_device_type")} {kwargs.get("ssh_username")}@{kwargs.get("ssh_host")}'
                )
                return res

        raise NetmikoAuthenticationException(
            f"all authentication attempts failed for {_kwargs.get('ssh_host')}"
        )
    else:
        return _connect(*args, **kwargs)


def _connect(*args, _requires=_get_missing_ssh_connection_vars, **kwargs):
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
        * *ssh_secret* (``bool``), ``optional`` --
           sets enable secret for auto enable



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
        "device_type": "linux",
        "port": 22,
    }

    use_jumphost = False

    if "jumphost_host" in kwargs:
        use_jumphost = True


    jumphost_cfg, opts = process_ssh_opts(kwargs, jumphost_defaults, "jumphost_")
    cfg, opts = process_ssh_opts(opts, defaults)

  

    if not cfg.get("session_log"):
        session_buffer = cfg["session_log"] = BytesIO()
    else:
        session_buffer = cfg.get("session_log")
        
    if cfg["verbose"]:
        netmiko_log.setLevel(logging.DEBUG)
    else:
        netmiko_log.setLevel(logging.ERROR)

    if use_jumphost:
        for var_name in ["username", "password"]:
            if not jumphost_cfg[var_name]:
                # try to inherit username and password from target host
                jumphost_cfg[var_name] = cfg.get(var_name)
            jumphost_cfg["ip"] = jumphost_cfg["host"]
            del jumphost_cfg["host"]

            try: 
                jumphost_cfg["session_log"]=session_buffer
                connection = ConnectHandler(**jumphost_cfg)
                log.debug(f"ssh {id(connection)}: successfully connected to jumphost {jumphost_cfg.get('ip')}")
                _save_as_last_working_cred_hash(jumphost_cfg.get('ip'),jumphost_cfg)
            except Exception as e:
                log.error(e)
                session_buffer.seek(0)
                log.error( f"ssh {id(connection)} session log:" + session_buffer.read().decode("utf-8", errors="ignore"))
                return None
            cfg["ip"] = cfg["host"]
            del cfg["host"]
            try:
                log.debug(f"ssh {id(connection)}: tying to jump to {cfg['username']}@{cfg['ip']}")
                connection.jump_to(**cfg)
            except:
                log.debug(f"ssh {id(connection)}: failed to jump to {cfg['username']}@{cfg['ip']}")
                session_buffer.seek(0)
                log.error( f"ssh {id(connection)}: session log:" + session_buffer.read().decode("utf-8", errors="ignore"))
                disconnect(connection)
                return ""
            log.debug(f"ssh {id(connection)}: successfully jumped to target to {cfg['username']}@{cfg['ip']}")
            _save_as_last_working_cred_hash(cfg.get('ip'),cfg)
            return connection

    else:
        try:
            cfg.update(opts)

            connection = ConnectHandler(**cfg)
            _save_as_last_working_cred_hash(cfg.get('host'),cfg)
            return connection
        except NetmikoAuthenticationException as e:
            session_buffer.seek(0)
            log.error( session_buffer.read().decode("utf-8", errors="ignore"))
            if _jinjamator.configuration["best_effort"]:
                _jinjamator._log.error(
                    f'ssh {id(connection)}: ssh {cfg["username"]}@{cfg["host"]}:{cfg["port"]}, login failed. Please check your credentials.'
                )
                return ""
            else:
                raise Exception(
                    f'ssh {id(connection)}: ssh {cfg["username"]}@{cfg["host"]}:{cfg["port"]}, login failed. Please check your credentials.'
                )


def query(
    command, connection=None, *, _requires=_get_missing_ssh_connection_vars, **kwargs
):
    if not connection:
        connection = connect(**kwargs)
        auto_disconnect = True
    
    cfg, opts = process_ssh_opts(kwargs, {}, "jumphost_")
    cfg, opts = process_ssh_opts(opts, {}, "ssh_")

    config = run(command, connection, **kwargs)

    return process(connection.device_type, command, config)


def disconnect(connection):
    try:
        if hasattr(connection,"__jump_device_list"):
            for _con in connection.__jump_device_list:
                log.debug(f"try to jump back {id(connection)}")
                connection.jump_back()
    except Exception as e:
        log.error(e)
    if connection:
        connection.cleanup()
    if connection:
        connection.paramiko_cleanup()
    log.debug(f"closed ssh connection {id(connection)}")

def run(
    command, connection=None, *, _requires=_get_missing_ssh_connection_vars, **kwargs
):
    auto_disconnect = False
    if not connection:
        connection = connect(**kwargs)
        auto_disconnect = True
    
    log.debug(f"ssh {id(connection)}: running command {command}")

    cfg, opts = process_ssh_opts(kwargs, {}, "jumphost_")
    cfg, opts = process_ssh_opts(opts, {}, "ssh_")


    retval = connection.send_command_expect(
        command, read_timeout=kwargs.get("read_timeout", 300), **opts
    )
    if auto_disconnect:
        disconnect(connection)
    log.debug(f"ssh {id(connection)}: result of command {retval}")
    # netmiko_log.setLevel(backup_log_level)
    return retval


def run_mlt(
    commands, connection=None, *, _requires=_get_missing_ssh_connection_vars, **kwargs
):
    auto_disconnect = False
    if not connection:
        connection = connect(**kwargs)
        auto_disconnect = True

    cfg, opts = process_ssh_opts(kwargs, {}, "jumphost_")
    cfg, opts = process_ssh_opts(opts, {}, "ssh_")
    log.debug(f"ssh {id(connection)}: running command {commands}")

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

    cfg, opts = process_ssh_opts(kwargs, {}, "jumphost_")
    cfg, opts = process_ssh_opts(opts, {}, "ssh_")

    retval = connection.send_config_set(commands, **opts)
    if kwargs.get("autosave",True):
        connection.save_config()

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

    cfg, opts = process_ssh_opts(kwargs, {}, "jumphost_")
    cfg, opts = process_ssh_opts(opts, {}, "ssh_")

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

    cfg, opts = process_ssh_opts(kwargs, {}, "jumphost_")
    cfg, opts = process_ssh_opts(opts, {}, "ssh_")

    scp = SCPConn(connection)
    scp.scp_put_file(src, dst)
    # Needed
    scp.close()
