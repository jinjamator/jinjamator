# Copyright 2026 pbe

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

# This plugin implements a subset of the Nextcloud WebDAV and OCS APIs, enough to
# support the file operations needed by jinjamator. It is not a full-featured
# Nextcloud client library but enables jinjamator to work with files in Nextcloud as
# if they were on a local filesystem (with few exceptions).

import logging
from urllib.parse import quote

log = logging.getLogger()

try:
    import requests
except ImportError:
    log.info("cannot load requests, nextcloud capability disabled. Install with: pip install requests")


class NextcloudConnection(object):
    """A thin authenticated handle for a single Nextcloud instance.

    Wraps a :class:`requests.Session` (carrying the HTTP Basic credentials) plus
    the pre-computed WebDAV and OCS endpoint roots, so the ``nextcloud.file.*``
    functions can issue requests without re-deriving URLs each time. Created by
    :func:`connect`; do not instantiate directly.

    :ivar base_url: The instance base URL with any trailing slash removed.
    :ivar username: The authenticated user name.
    :ivar session: The underlying :class:`requests.Session`.
    :ivar webdav_root: WebDAV files root for ``username``.
    :ivar ocs_url: OCS API v2 base URL.
    """

    def __init__(self, base_url, username, session, timeout=30, dav_user=None):
        self.base_url = base_url.rstrip("/")
        self.username = username
        # Nextcloud's WebDAV path is keyed by the internal user *id*, which is
        # not always the login name (it can be a GUID for LDAP/SSO accounts).
        self.dav_user = dav_user or username
        self.session = session
        self.timeout = timeout
        self.webdav_root = f"{self.base_url}/remote.php/dav/files/{self.dav_user}"
        self.ocs_url = f"{self.base_url}/ocs/v2.php"

    def webdav_path(self, remote_path):
        """Return the fully-qualified, URL-quoted WebDAV URL for ``remote_path``."""
        segments = [s for s in str(remote_path).strip("/").split("/") if s != ""]
        quoted = "/".join(quote(s) for s in segments)
        return f"{self.webdav_root}/{quoted}" if quoted else self.webdav_root


def _get_missing_nextcloud_connection_vars():
    """Return the Nextcloud connection variables jinjamator must still gather.

    Dependency-injection hook wired into :func:`connect` via its ``_requires``
    default. For every name returned, jinjamator prompts (CLI) or generates a
    web-form field (daemon) while analyzing a tasklet. Inspects the task
    *configuration* only; values passed inline as keyword arguments are resolved
    separately by the static analyzer.

    :return: Names of the still-missing ``nextcloud_*`` configuration variables.
    :rtype: ``list`` of ``str``
    """
    inject = []
    try:
        if not _jinjamator.configuration._data.get("nextcloud_url"):
            inject.append("nextcloud_url")
        if not _jinjamator.configuration._data.get("nextcloud_username"):
            inject.append("nextcloud_username")
        if not _jinjamator.configuration._data.get("nextcloud_password"):
            inject.append("nextcloud_password")
    except Exception as e:
        log.error(e)
    return inject


def process_nextcloud_opts(
    kwargs,
    defaults=None,
    prefix="nextcloud_",
    variables_to_parse=["url", "username", "password", "verify_ssl", "timeout"],
):
    """Split ``nextcloud_*`` connection options out of a kwargs dict.

    For every name in ``variables_to_parse`` the value is resolved with the
    precedence **explicit keyword argument > task configuration > defaults**, and
    the consumed keys are popped from ``kwargs``.

    :param kwargs: Keyword arguments of the calling plugin function. Mutated --
        recognised ``nextcloud_*`` keys are popped out.
    :type kwargs: ``dict``
    :param defaults: Fallback values keyed by the unprefixed option name.
    :type defaults: ``dict``
    :param prefix: Configuration/keyword prefix to strip, defaults to ``nextcloud_``.
    :type prefix: ``str``
    :param variables_to_parse: Unprefixed option names to extract.
    :type variables_to_parse: ``list`` of ``str``
    :return: A ``(cfg, kwargs)`` tuple -- ``cfg`` holds the resolved connection
        options (unprefixed keys, ``None`` removed), ``kwargs`` the remainder.
    :rtype: ``tuple`` (``dict``, ``dict``)

    :Examples:

        .. code-block:: python

            cfg, opts = process_nextcloud_opts(
                {"nextcloud_url": "https://fileflux.eu", "nextcloud_username": "nwtest"}
            )
            # cfg -> {'url': 'https://fileflux.eu', 'username': 'nwtest'}
    """
    defaults = defaults or {}
    cfg = {}
    for var_name in variables_to_parse:
        cfg[var_name] = kwargs.get(
            f"{prefix}{var_name}",
            _jinjamator.configuration.get(f"{prefix}{var_name}", defaults.get(var_name)),
        )
        kwargs.pop(prefix + var_name, None)
        kwargs.pop(var_name, None)
    cfg = {k: v for k, v in cfg.items() if v is not None}
    return cfg, kwargs


def connect(*args, _requires=_get_missing_nextcloud_connection_vars, **kwargs):
    """Authenticate against a Nextcloud instance and return a reusable handle.

    The returned :class:`NextcloudConnection` can be passed to the
    ``nextcloud.file.*`` functions via their ``connection`` argument to reuse a
    single authenticated session for many operations. Authentication uses HTTP
    Basic -- a Nextcloud **app password** works in place of the account
    password and is the recommended credential. The connection is validated
    immediately with a ``PROPFIND`` against the user's WebDAV root.

    This is the only function in the plugin carrying the ``_requires`` hook, so a
    missing ``nextcloud_url`` / ``nextcloud_username`` / ``nextcloud_password``
    causes jinjamator to prompt (see :func:`_get_missing_nextcloud_connection_vars`).

    :param args: Ignored positional arguments (accepted for call-site symmetry).
    :return: An authenticated Nextcloud connection handle.
    :rtype: :class:`NextcloudConnection`
    :raises Exception: If authentication or the connectivity check fails.

    :Keyword Arguments:
        * *nextcloud_url* (``str``), ``jinjamator enforced`` -- base URL of the
          instance, e.g. ``https://fileflux.eu``.
        * *nextcloud_username* (``str``), ``jinjamator enforced`` -- login user.
        * *nextcloud_password* (``str``), ``jinjamator enforced`` -- account or
          app password.
        * *nextcloud_verify_ssl* (``bool``) -- verify the TLS certificate,
          defaults to ``True``.
        * *nextcloud_timeout* (``int``) -- per-request timeout in seconds,
          defaults to 30.

    :Examples:

        .. code-block:: python

            conn = nextcloud.connect(
                nextcloud_url='https://fileflux.eu',
                nextcloud_username='nwtest',
                nextcloud_password='app-password',
            )
            nextcloud.file.mkdir('/demo', connection=conn)
            nextcloud.disconnect(conn)
    """
    cfg, opts = process_nextcloud_opts(kwargs, {"verify_ssl": True, "timeout": 30})
    for required in ("url", "username", "password"):
        if not cfg.get(required):
            raise ValueError(f"nextcloud: no nextcloud_{required} given, cannot connect")

    session = requests.Session()
    session.auth = (cfg["username"], cfg["password"])
    session.verify = cfg.get("verify_ssl", True)
    base_url = cfg["url"].rstrip("/")
    timeout = cfg.get("timeout", 30)

    # Authenticate and resolve the real WebDAV user id in one call: the OCS
    # cloud/user endpoint returns the internal id used in the dav files path.
    log.debug(f"nextcloud: authenticating {cfg['username']}@{base_url}")
    resp = session.get(
        f"{base_url}/ocs/v2.php/cloud/user",
        headers={"OCS-APIRequest": "true", "Accept": "application/json"},
        timeout=timeout,
    )
    if resp.status_code in (401, 403):
        raise Exception(
            f"nextcloud: authentication failed for {cfg['username']}@{base_url} "
            f"(HTTP {resp.status_code})"
        )
    if resp.status_code >= 400:
        raise Exception(
            f"nextcloud: connectivity check failed for {base_url} (HTTP {resp.status_code})"
        )
    dav_user = cfg["username"]
    try:
        data = resp.json().get("ocs", {}).get("data", {})
        if data.get("id"):
            dav_user = data["id"]
    except ValueError:
        log.debug("nextcloud: cloud/user did not return JSON, falling back to login name")

    connection = NextcloudConnection(
        base_url, cfg["username"], session, timeout=timeout, dav_user=dav_user
    )
    log.debug(
        f"nextcloud: successfully connected {cfg['username']}@{base_url} "
        f"(dav user id: {dav_user})"
    )
    return connection


def disconnect(connection):
    """Close a Nextcloud connection opened with :func:`connect`.

    Closes the underlying :class:`requests.Session`. Safe to call with ``None``
    and never raises. ``nextcloud.file.*`` functions that open their own
    short-lived connection close it automatically, so you only need this for
    connections you opened yourself.

    :param connection: The handle returned by :func:`connect`, or ``None``.
    :type connection: :class:`NextcloudConnection` or ``None``
    :return: Nothing.
    :rtype: ``None``

    :Examples:

        .. code-block:: python

            conn = nextcloud.connect(nextcloud_url='https://fileflux.eu',
                                     nextcloud_username='nwtest', nextcloud_password='app-pw')
            try:
                nextcloud.file.mkdir('/demo', connection=conn)
            finally:
                nextcloud.disconnect(conn)
    """
    if not connection:
        return
    try:
        connection.session.close()
    except Exception as e:
        log.debug(f"nextcloud: error while closing session: {e}")
    log.debug(f"nextcloud: closed connection {id(connection)}")
