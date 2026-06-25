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
import os
from copy import deepcopy

log = logging.getLogger()

try:
    from pypsrp.client import Client
except ImportError:
    log.info(
        "cannot load pypsrp, winrm/powershell remote capability disabled. "
        "Install with: pip install pypsrp"
    )


def _get_missing_winrm_connection_vars():
    """Return the list of WinRM connection variables jinjamator must still gather.

    This is the dependency-injection hook wired into :func:`connect` via its
    ``_requires`` keyword default. While analyzing a tasklet jinjamator calls
    this function and, for every variable name it returns, either prompts the
    user (CLI mode) or generates an input field in the auto-built web form
    (daemon mode). It inspects the *task configuration* only -- values passed
    inline as keyword arguments are resolved separately by the static analyzer.

    Mirrors the ssh content plugin: when ``winrm_credentials`` is present the
    credentials are validated at runtime, so nothing is enforced up front and an
    empty list is returned. Otherwise ``winrm_host``, ``winrm_username`` and
    ``winrm_password`` are required.

    :return: Names of the still-missing ``winrm_*`` configuration variables.
    :rtype: ``list`` of ``str``

    :Examples:

        Used as the ``_requires`` hook -- you normally never call it directly:

            .. code-block:: python

                def connect(*args, _requires=_get_missing_winrm_connection_vars, **kwargs):
                    ...

        Its return value drives the prompt, e.g. with an empty configuration:

            .. code-block:: python

                _get_missing_winrm_connection_vars()
                # -> ['winrm_username', 'winrm_password', 'winrm_host']
    """
    inject = []
    if _jinjamator.configuration._data.get("winrm_credentials"):
        return inject
    try:
        if not _jinjamator.configuration._data.get("winrm_username"):
            inject.append("winrm_username")
        if not _jinjamator.configuration._data.get("winrm_password"):
            inject.append("winrm_password")
        if not _jinjamator.configuration._data.get("winrm_host"):
            inject.append("winrm_host")
    except Exception as e:
        log.error(e)
    return inject


def process_winrm_opts(
    kwargs,
    defaults,
    prefix="winrm_",
    variables_to_parse=[
        "host",
        "username",
        "password",
        "port",
        "ssl",
        "auth",
        "cert_validation",
        "path",
        "connection_timeout",
        "operation_timeout",
        "read_timeout",
        "encryption",
        "negotiate_service",
        "negotiate_hostname_override",
    ],
):
    """Split connection options out of a kwargs dict and resolve their values.

    For every name in ``variables_to_parse`` the value is looked up with the
    precedence **explicit keyword argument > task configuration > defaults**, the
    consumed keys are removed from ``kwargs``, and the result is returned as a
    clean ``cfg`` dict ready to hand to pypsrp's :class:`~pypsrp.client.Client`.
    ``None`` values are dropped from ``cfg`` so pypsrp can apply its own defaults
    (for example deriving the port from ``ssl``). As a convenience
    ``winrm_authentication`` is accepted as an alias for ``winrm_auth``.

    :param kwargs: The keyword arguments passed to the calling plugin function.
        This dict is mutated -- recognised ``winrm_*`` keys are popped out.
    :type kwargs: ``dict``
    :param defaults: Fallback values keyed by the *unprefixed* option name
        (e.g. ``{"ssl": False, "auth": "negotiate"}``).
    :type defaults: ``dict``
    :param prefix: The configuration/keyword prefix to strip, defaults to
        ``"winrm_"``.
    :type prefix: ``str``
    :param variables_to_parse: Unprefixed option names to extract. Defaults to
        the full set of pypsrp connection parameters.
    :type variables_to_parse: ``list`` of ``str``
    :return: A ``(cfg, kwargs)`` tuple -- ``cfg`` holds the resolved connection
        options (unprefixed keys, ``None`` removed), ``kwargs`` holds whatever
        was left over after the connection keys were popped.
    :rtype: ``tuple`` (``dict``, ``dict``)

    :Examples:

        .. code-block:: python

            cfg, opts = process_winrm_opts(
                {"winrm_host": "win01", "winrm_authentication": "ntlm", "extra": 1},
                {"ssl": False, "auth": "negotiate"},
            )
            # cfg  -> {'host': 'win01', 'ssl': False, 'auth': 'ntlm'}
            # opts -> {'extra': 1}
    """
    cfg = {}
    for key in ("winrm_credentials", "winrm_max_concurrency"):
        kwargs.pop(key, None)

    # accept "authentication" as a friendlier alias for pypsrp's "auth"
    auth_alias = kwargs.pop(f"{prefix}authentication", None) or _jinjamator.configuration.get(
        f"{prefix}authentication"
    )
    if auth_alias is not None and kwargs.get(f"{prefix}auth") is None:
        kwargs[f"{prefix}auth"] = auth_alias

    for var_name in variables_to_parse:
        cfg[var_name] = kwargs.get(
            f"{prefix}{var_name}",
            _jinjamator.configuration.get(
                f"{prefix}{var_name}", defaults.get(var_name)
            ),
        )
        kwargs.pop(prefix + var_name, None)
        kwargs.pop(var_name, None)

    cfg = {k: v for k, v in cfg.items() if v is not None}
    return cfg, kwargs


def _build_client(**kwargs):
    """Build a pypsrp :class:`~pypsrp.client.Client` from ``winrm_*`` options.

    Applies the plugin's connection defaults (plain HTTP on port 5985,
    ``negotiate`` auth, certificate validation disabled), resolves the final
    values through :func:`process_winrm_opts`, and instantiates the client.
    Note that pypsrp does **not** open a socket or authenticate here -- that
    happens lazily on the first command; use :func:`_mplexed_connect` when you
    need an eagerly validated connection.

    :raises ValueError: If no ``winrm_host`` could be resolved.
    :return: A configured, not-yet-authenticated pypsrp client.
    :rtype: :class:`pypsrp.client.Client`

    :Keyword Arguments:
        Accepts the same ``winrm_*`` keys as :func:`connect` (see there).

    :Examples:

        .. code-block:: python

            client = _build_client(
                winrm_host="192.168.11.122",
                winrm_username="script",
                winrm_password="secret",
                winrm_auth="ntlm",
            )
    """
    defaults = {
        "ssl": False,
        "auth": "negotiate",
        "cert_validation": False,
        "path": "wsman",
        "connection_timeout": 30,
    }
    cfg, opts = process_winrm_opts(kwargs, defaults)
    server = cfg.pop("host", None)
    if not server:
        raise ValueError("winrm: no winrm_host given, cannot connect")
    log.debug(
        f"winrm: connecting to {cfg.get('username')}@{server} "
        f"(ssl={cfg.get('ssl')}, auth={cfg.get('auth')})"
    )
    return Client(server, **cfg)


def _mplexed_connect(**kwargs):
    """Build a client and eagerly validate it with a trivial probe command.

    Because pypsrp authenticates lazily, this helper runs a no-op PowerShell
    statement (``$true | Out-Null``) to force the WinRM/authentication handshake
    immediately. It is used by :func:`connect` when iterating over
    ``winrm_credentials`` so that a failing credential can be detected and the
    next one tried, rather than failing later on the first real command. All
    exceptions are swallowed and turned into a ``None`` return.

    :Keyword Arguments:
        Accepts the same ``winrm_*`` keys as :func:`connect` (see there).

    :return: A connected, authenticated client, or ``None`` if the probe failed.
    :rtype: :class:`pypsrp.client.Client` or ``None``

    :Examples:

        .. code-block:: python

            client = _mplexed_connect(
                winrm_host="192.168.11.122",
                winrm_username="script",
                winrm_password="wrong-password",
            )
            # client is None because authentication failed
    """
    try:
        client = _build_client(**kwargs)
        client.execute_ps("$true | Out-Null")
        return client
    except Exception as e:
        log.info(str(e))
        log.info(
            f'cannot connect using winrm {kwargs.get("winrm_username")}@'
            f'{kwargs.get("winrm_host")}, skipping this variant'
        )
        return None


def connect(*args, _requires=_get_missing_winrm_connection_vars, **kwargs):
    """Connect to a Windows host via WinRM/PSRP and return a reusable client.

    This is the entry point for opening a session. The returned client can be
    handed to :func:`run`, :func:`run_cmd`, :func:`put_file` and
    :func:`get_file` via their ``connection`` argument to reuse a single
    authenticated session for many operations; remember to close it with
    :func:`disconnect` when done.

    If ``winrm_credentials`` (a list of ``winrm_*`` dicts) is supplied, each
    credential set is tried in order until one authenticates -- mirroring the
    ssh content plugin's credential rotation. Otherwise a single connection is
    built from the task configuration merged with the keyword arguments.

    This is also the only function in the plugin that carries the
    ``_requires`` dependency hook, so missing ``winrm_host`` / ``winrm_username``
    / ``winrm_password`` cause jinjamator to prompt for them (see
    :func:`_get_missing_winrm_connection_vars`).

    :param args: Ignored positional arguments (accepted for call-site symmetry).
    :return: An authenticated WinRM client.
    :rtype: :class:`pypsrp.client.Client`
    :raises Exception: If every credential in ``winrm_credentials`` fails.
    :raises ValueError: If no ``winrm_host`` is provided.

    :Keyword Arguments:
        * *winrm_host* (``str``), ``jinjamator enforced`` -- target hostname or IP.
        * *winrm_username* (``str``), ``jinjamator enforced`` -- logon user. For a
          local (non-domain) account NTLM is usually required.
        * *winrm_password* (``str``), ``jinjamator enforced`` -- logon password.
        * *winrm_port* (``int``) -- WinRM TCP port. Defaults to 5985 (HTTP) or
          5986 when ``winrm_ssl`` is set.
        * *winrm_ssl* (``bool``) -- use the HTTPS transport. Defaults to ``False``.
        * *winrm_auth* (``str``) -- authentication mechanism: ``negotiate``,
          ``ntlm``, ``kerberos``, ``credssp``, ``basic`` or ``certificate``.
          Defaults to ``negotiate``.
        * *winrm_authentication* (``str``) -- friendly alias for ``winrm_auth``.
        * *winrm_cert_validation* (``bool``) -- validate the server certificate
          when using SSL. Defaults to ``False``.
        * *winrm_path* (``str``) -- WSMan URL path. Defaults to ``wsman``.
        * *winrm_connection_timeout* (``int``) -- TCP/HTTP connect timeout in
          seconds. Defaults to 30.
        * *winrm_operation_timeout* (``int``) -- WSMan operation timeout in seconds.
        * *winrm_read_timeout* (``int``) -- HTTP read timeout in seconds.
        * *winrm_encryption* (``str``) -- message encryption mode: ``auto``,
          ``always`` or ``never``.
        * *winrm_negotiate_service* (``str``) -- SPN service for Negotiate/Kerberos.
        * *winrm_negotiate_hostname_override* (``str``) -- SPN hostname override.
        * *winrm_credentials* (``list``) -- list of ``winrm_*`` dicts to try in
          order until one authenticates.

    :Examples:

        Open a session, run several commands, then close it.

        python tasklet:

            .. code-block:: python

                conn = winrm.connect(
                    winrm_host='192.168.11.122',
                    winrm_username='script',
                    winrm_password='secret',
                    winrm_authentication='ntlm',
                )
                hostname = winrm.run('$env:COMPUTERNAME', connection=conn)
                winrm.disconnect(conn)
                return hostname

        Try several credential sets until one works:

            .. code-block:: python

                conn = winrm.connect(winrm_host='192.168.11.122', winrm_credentials=[
                    {'winrm_username': 'admin', 'winrm_password': 'pw1', 'winrm_auth': 'ntlm'},
                    {'winrm_username': 'script', 'winrm_password': 'pw2', 'winrm_auth': 'ntlm'},
                ])
    """
    if "winrm_credentials" in kwargs:
        last = None
        for attempt, cred in enumerate(kwargs["winrm_credentials"], 1):
            _kwargs = deepcopy(kwargs)
            del _kwargs["winrm_credentials"]
            _kwargs.update(cred)
            last = _kwargs
            client = _mplexed_connect(**_kwargs)
            if client:
                log.debug(
                    f'winrm: successfully connected (attempt {attempt}) '
                    f'{_kwargs.get("winrm_username")}@{_kwargs.get("winrm_host")}'
                )
                return client
        raise Exception(
            f"winrm: all authentication attempts failed for "
            f"{(last or kwargs).get('winrm_host')}"
        )
    return _build_client(**kwargs)


def disconnect(connection):
    """Close a WinRM connection opened with :func:`connect`.

    Releases the underlying pypsrp/WSMan transport. Safe to call with ``None``
    (no-op) and never raises -- transport-close errors are only logged at debug
    level. Functions such as :func:`run` that open their own short-lived
    connection call this automatically, so you only need it for sessions you
    opened yourself via :func:`connect`.

    :param connection: The client returned by :func:`connect`, or ``None``.
    :type connection: :class:`pypsrp.client.Client` or ``None``
    :return: Nothing.
    :rtype: ``None``

    :Examples:

        .. code-block:: python

            conn = winrm.connect(winrm_host='192.168.11.122', winrm_username='script', winrm_password='secret')
            try:
                winrm.run('Get-Date', connection=conn)
            finally:
                winrm.disconnect(conn)
    """
    if not connection:
        return
    try:
        connection.close()
    except Exception as e:
        log.debug(f"winrm: error while closing connection: {e}")
    log.debug(f"winrm: closed connection {id(connection)}")


def run(
    script,
    connection=None,
    **kwargs,
):
    """Run a PowerShell script on a remote Windows host and return its output.

    The script is executed through PSRP (a real PowerShell runspace), so
    PowerShell cmdlets, pipelines and language features are available -- use
    :func:`run_cmd` if you need genuine ``cmd.exe`` semantics instead. If no
    ``connection`` is given one is opened from the supplied/configured
    ``winrm_*`` values and closed again afterwards; pass a ``connection`` from
    :func:`connect` to reuse a session across several calls.

    By default any PowerShell error stream entry raises an exception. When the
    task sets ``best_effort`` the errors are logged instead and the (partial)
    output is returned.

    :param script: The PowerShell script / command to execute.
    :type script: ``str``
    :param connection: An existing session from :func:`connect`. If omitted, a
        throwaway connection is opened and closed around this call.
    :type connection: :class:`pypsrp.client.Client` or ``None``
    :return: The textual PowerShell output. With ``return_streams=True`` a
        ``(output, streams, had_errors)`` tuple is returned instead, where
        ``streams`` exposes ``.error``, ``.warning``, ``.verbose``, ``.debug``
        and ``.information``.
    :rtype: ``str`` or ``tuple``
    :raises Exception: If the script writes to the PowerShell error stream and
        ``best_effort`` is not set on the task.

    :Keyword Arguments:
        * *return_streams* (``bool``) -- return the full
          ``(output, streams, had_errors)`` tuple instead of just the text.
        * Any ``winrm_*`` connection key accepted by :func:`connect` -- only
          used when ``connection`` is not supplied.

    :Examples:

        jinja2 tasklet (connection params come from task configuration):

            .. code-block:: jinja

                {{ winrm.run('Get-Service | Where-Object {$_.Status -eq "Running"}') }}

        python tasklet, reusing an explicit connection:

            .. code-block:: python

                conn = winrm.connect(winrm_host='1.2.3.4', winrm_username='admin', winrm_password='secret')
                return winrm.run('Get-Process | Select-Object -First 5', connection=conn)

        python tasklet, inspecting the error/warning streams:

            .. code-block:: python

                out, streams, had_errors = winrm.run('Get-Item C:\\missing', return_streams=True)
    """
    return_streams = kwargs.pop("return_streams", False)
    auto_disconnect = False
    if not connection:
        connection = connect(**kwargs)
        auto_disconnect = True

    log.debug(f"winrm {id(connection)}: running powershell script {script}")
    try:
        output, streams, had_errors = connection.execute_ps(script)
    finally:
        if auto_disconnect:
            disconnect(connection)

    if had_errors:
        errors = "\n".join(str(e) for e in streams.error)
        if _jinjamator.configuration.get("best_effort"):
            _jinjamator._log.error(f"winrm {id(connection)}: powershell errors:\n{errors}")
        else:
            raise Exception(f"winrm: powershell script reported errors:\n{errors}")

    log.debug(f"winrm {id(connection)}: result of script {output}")
    if return_streams:
        return output, streams, had_errors
    return output


def run_cmd(
    command,
    connection=None,
    **kwargs,
):
    """Run a ``cmd.exe`` command on a remote Windows host.

    This runs the command through the legacy command processor (not PowerShell),
    which is the right choice for classic console tools that depend on
    ``cmd.exe`` quoting and exit-code behaviour. As with :func:`run`, a
    ``connection`` is reused if given, otherwise a throwaway one is opened from
    the ``winrm_*`` values and closed afterwards.

    By default a non-zero exit code raises an exception. When the task sets
    ``best_effort`` the failure is logged instead and the captured stdout is
    returned.

    :param command: The ``cmd.exe`` command line to execute.
    :type command: ``str``
    :param connection: An existing session from :func:`connect`. If omitted, a
        throwaway connection is opened and closed around this call.
    :type connection: :class:`pypsrp.client.Client` or ``None``
    :return: The command's stdout. With ``return_all=True`` a
        ``(stdout, stderr, return_code)`` tuple is returned instead.
    :rtype: ``str`` or ``tuple``
    :raises Exception: If the command returns a non-zero exit code and
        ``best_effort`` is not set on the task.

    :Keyword Arguments:
        * *return_all* (``bool``) -- return the full
          ``(stdout, stderr, return_code)`` tuple instead of just stdout.
        * Any ``winrm_*`` connection key accepted by :func:`connect` -- only
          used when ``connection`` is not supplied.

    :Examples:

        python tasklet:

            .. code-block:: python

                conn = winrm.connect(winrm_host='1.2.3.4', winrm_username='admin', winrm_password='secret')
                return winrm.run_cmd('ipconfig /all', connection=conn)

        capturing the return code:

            .. code-block:: python

                stdout, stderr, rc = winrm.run_cmd('whoami /priv', connection=conn, return_all=True)
    """
    return_all = kwargs.pop("return_all", False)
    auto_disconnect = False
    if not connection:
        connection = connect(**kwargs)
        auto_disconnect = True

    log.debug(f"winrm {id(connection)}: running cmd command {command}")
    try:
        stdout, stderr, rc = connection.execute_cmd(command)
    finally:
        if auto_disconnect:
            disconnect(connection)

    if rc != 0:
        if _jinjamator.configuration.get("best_effort"):
            _jinjamator._log.error(
                f"winrm {id(connection)}: command exited {rc}, stderr:\n{stderr}"
            )
        else:
            raise Exception(
                f"winrm: command '{command}' exited with code {rc}, stderr:\n{stderr}"
            )

    if return_all:
        return stdout, stderr, rc
    return stdout


def put_file(
    src,
    dst,
    connection=None,
    **kwargs,
):
    """Copy a local file up to the remote Windows host.

    Streams the file to the target over WinRM using pypsrp's
    :meth:`~pypsrp.client.Client.copy`. A ``connection`` is reused if given,
    otherwise a throwaway one is opened from the ``winrm_*`` values and closed
    afterwards.

    :param src: Path of the local source file to upload.
    :type src: ``str``
    :param dst: Destination path on the remote Windows host (e.g.
        ``C:\\temp\\file.txt``).
    :type dst: ``str``
    :param connection: An existing session from :func:`connect`. If omitted, a
        throwaway connection is opened and closed around this call.
    :type connection: :class:`pypsrp.client.Client` or ``None``
    :return: The resolved remote destination path reported by pypsrp.
    :rtype: ``str``

    :Keyword Arguments:
        Any ``winrm_*`` connection key accepted by :func:`connect` -- only used
        when ``connection`` is not supplied.

    :Examples:

        python tasklet:

            .. code-block:: python

                conn = winrm.connect(winrm_host='1.2.3.4', winrm_username='admin', winrm_password='secret')
                winrm.put_file('/tmp/payload.ps1', 'C:\\temp\\payload.ps1', connection=conn)
    """
    auto_disconnect = False
    if not connection:
        connection = connect(**kwargs)
        auto_disconnect = True
    try:
        log.debug(f"winrm {id(connection)}: copying {src} -> {dst}")
        return connection.copy(src, dst)
    finally:
        if auto_disconnect:
            disconnect(connection)


def get_file(
    src,
    dst,
    connection=None,
    **kwargs,
):
    """Download a file from the remote Windows host to the local machine.

    Streams the remote file down over WinRM using pypsrp's
    :meth:`~pypsrp.client.Client.fetch`. A ``connection`` is reused if given,
    otherwise a throwaway one is opened from the ``winrm_*`` values and closed
    afterwards.

    :param src: Path of the source file on the remote Windows host (e.g.
        ``C:\\temp\\result.txt``).
    :type src: ``str``
    :param dst: Local destination path to write the downloaded file to.
    :type dst: ``str``
    :param connection: An existing session from :func:`connect`. If omitted, a
        throwaway connection is opened and closed around this call.
    :type connection: :class:`pypsrp.client.Client` or ``None``
    :return: Nothing -- the file is written to ``dst``.
    :rtype: ``None``

    :Keyword Arguments:
        Any ``winrm_*`` connection key accepted by :func:`connect` -- only used
        when ``connection`` is not supplied.

    :Examples:

        python tasklet:

            .. code-block:: python

                conn = winrm.connect(winrm_host='1.2.3.4', winrm_username='admin', winrm_password='secret')
                winrm.get_file('C:\\temp\\result.txt', '/tmp/result.txt', connection=conn)
    """
    auto_disconnect = False
    if not connection:
        connection = connect(**kwargs)
        auto_disconnect = True
    try:
        log.debug(f"winrm {id(connection)}: fetching {src} -> {dst}")
        connection.fetch(src, dst)
    finally:
        if auto_disconnect:
            disconnect(connection)
