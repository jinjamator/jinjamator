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

import logging
import os
import posixpath
import fnmatch
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from jinjamator.plugins.content import nextcloud as ncbackend

log = logging.getLogger()

# keep a handle on the builtin: this module defines its own open() below
py_open = open

# Nextcloud share types (OCS Share API)
SHARE_TYPE_USER = 0
SHARE_TYPE_GROUP = 1
SHARE_TYPE_PUBLIC_LINK = 3
SHARE_TYPE_EMAIL = 4
SHARE_TYPE_FEDERATED = 6


def _resolve_connection(connection, kwargs):
    """Return ``(connection, auto_close)``, opening a throwaway one if needed.

    If ``connection`` is given it is reused and ``auto_close`` is ``False``;
    otherwise a new connection is built from the remaining ``nextcloud_*``
    keyword arguments / task configuration and ``auto_close`` is ``True`` so the
    caller knows to disconnect it.
    """
    if connection is not None:
        return connection, False
    return ncbackend.connect(**kwargs), True


def _mkcol(conn, path):
    """Issue a single WebDAV ``MKCOL`` for ``path``; tolerate "already exists"."""
    url = conn.webdav_path(path)
    resp = conn.session.request("MKCOL", url, timeout=conn.timeout)
    if resp.status_code == 201:
        log.debug(f"nextcloud.file.mkdir: created {path}")
        return True
    if resp.status_code == 405:  # Method Not Allowed -> collection already exists
        log.debug(f"nextcloud.file.mkdir: {path} already exists")
        return True
    raise Exception(
        f"nextcloud.file.mkdir: failed to create '{path}' (HTTP {resp.status_code})"
    )


def mkdir(path, connection=None, recursive=True, **kwargs):
    """Create a directory (WebDAV collection) on the Nextcloud instance.

    :param path: Remote directory path, relative to the user's files root, e.g.
        ``/jinjamator_test`` or ``foo/bar``.
    :type path: ``str``
    :param connection: An existing handle from :func:`nextcloud.connect`. If
        omitted, one is opened from the ``nextcloud_*`` values and closed again.
    :type connection: :class:`NextcloudConnection` or ``None``
    :param recursive: Create intermediate parent directories as needed. WebDAV
        ``MKCOL`` only creates one level, so each segment is created in turn.
        Defaults to ``True``.
    :type recursive: ``bool``
    :return: ``True`` on success (creating an existing directory is a no-op).
    :rtype: ``bool``
    :raises Exception: If the directory could not be created.

    :Keyword Arguments:
        Any ``nextcloud_*`` connection key accepted by :func:`nextcloud.connect`
        -- only used when ``connection`` is not supplied.

    :Examples:

        .. code-block:: python

            conn = nextcloud.connect(nextcloud_url='https://fileflux.eu',
                                     nextcloud_username='nwtest', nextcloud_password='app-pw')
            nextcloud.file.mkdir('/jinjamator_test/sub', connection=conn)
    """
    conn, auto = _resolve_connection(connection, kwargs)
    try:
        if recursive:
            cumulative = ""
            result = None
            for seg in [s for s in str(path).strip("/").split("/") if s]:
                cumulative += "/" + seg
                result = _mkcol(conn, cumulative)
            return result if result is not None else True
        return _mkcol(conn, path)
    finally:
        if auto:
            ncbackend.disconnect(conn)


def put(local_path, remote_path, connection=None, create_parents=True, **kwargs):
    """Upload a local file to the Nextcloud instance via WebDAV ``PUT``.

    :param local_path: Path to the local source file.
    :type local_path: ``str``
    :param remote_path: Destination path on Nextcloud, relative to the user's
        files root, e.g. ``/jinjamator_test/hello.txt``.
    :type remote_path: ``str``
    :param connection: An existing handle from :func:`nextcloud.connect`. If
        omitted, one is opened from the ``nextcloud_*`` values and closed again.
    :type connection: :class:`NextcloudConnection` or ``None``
    :param create_parents: Create the remote parent directory first if missing.
        Defaults to ``True``.
    :type create_parents: ``bool``
    :return: ``True`` on success.
    :rtype: ``bool``
    :raises Exception: If the upload fails.
    :raises FileNotFoundError: If ``local_path`` does not exist.

    :Keyword Arguments:
        Any ``nextcloud_*`` connection key accepted by :func:`nextcloud.connect`
        -- only used when ``connection`` is not supplied.

    :Examples:

        .. code-block:: python

            nextcloud.file.put('/tmp/report.pdf', '/jinjamator_test/report.pdf', connection=conn)
    """
    conn, auto = _resolve_connection(connection, kwargs)
    try:
        if create_parents:
            parent = os.path.dirname(str(remote_path).rstrip("/"))
            if parent and parent.strip("/"):
                mkdir(parent, connection=conn)
        with py_open(local_path, "rb") as fh:
            data = fh.read()
        url = conn.webdav_path(remote_path)
        resp = conn.session.put(url, data=data, timeout=conn.timeout)
        if resp.status_code not in (200, 201, 204):
            raise Exception(
                f"nextcloud.file.put: upload of '{local_path}' -> '{remote_path}' "
                f"failed (HTTP {resp.status_code})"
            )
        log.debug(f"nextcloud.file.put: uploaded {local_path} -> {remote_path}")
        return True
    finally:
        if auto:
            ncbackend.disconnect(conn)


def get(remote_path, local_path, connection=None, **kwargs):
    """Download a file from the Nextcloud instance via WebDAV ``GET``.

    :param remote_path: Source path on Nextcloud, relative to the user's files
        root, e.g. ``/jinjamator_test/hello.txt``.
    :type remote_path: ``str``
    :param local_path: Local destination path to write the file to.
    :type local_path: ``str``
    :param connection: An existing handle from :func:`nextcloud.connect`. If
        omitted, one is opened from the ``nextcloud_*`` values and closed again.
    :type connection: :class:`NextcloudConnection` or ``None``
    :return: The local destination path that was written.
    :rtype: ``str``
    :raises Exception: If the download fails.

    :Keyword Arguments:
        Any ``nextcloud_*`` connection key accepted by :func:`nextcloud.connect`
        -- only used when ``connection`` is not supplied.

    :Examples:

        .. code-block:: python

            nextcloud.file.get('/jinjamator_test/report.pdf', '/tmp/report.pdf', connection=conn)
    """
    conn, auto = _resolve_connection(connection, kwargs)
    try:
        url = conn.webdav_path(remote_path)
        resp = conn.session.get(url, timeout=conn.timeout, stream=True)
        if resp.status_code != 200:
            raise Exception(
                f"nextcloud.file.get: download of '{remote_path}' failed "
                f"(HTTP {resp.status_code})"
            )
        with py_open(local_path, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)
        log.debug(f"nextcloud.file.get: downloaded {remote_path} -> {local_path}")
        return local_path
    finally:
        if auto:
            ncbackend.disconnect(conn)


def share(
    path,
    connection=None,
    share_type=SHARE_TYPE_PUBLIC_LINK,
    permissions=None,
    password=None,
    public_upload=None,
    expire_date=None,
    share_with=None,
    **kwargs,
):
    """Share a file or directory via the Nextcloud OCS Share API.

    Creates a share for ``path`` and returns the resulting share record. For the
    default public-link share (``share_type=3``) the record's ``url`` field holds
    the shareable link.

    :param path: Remote path to share, relative to the user's files root, e.g.
        ``/jinjamator_test`` or ``/jinjamator_test/report.pdf``.
    :type path: ``str``
    :param connection: An existing handle from :func:`nextcloud.connect`. If
        omitted, one is opened from the ``nextcloud_*`` values and closed again.
    :type connection: :class:`NextcloudConnection` or ``None``
    :param share_type: OCS share type: ``0`` user, ``1`` group, ``3`` public
        link, ``4`` email, ``6`` federated. Defaults to ``3`` (public link).
    :type share_type: ``int``
    :param permissions: Optional permission bitmask (1 read, 2 update, 4 create,
        8 delete, 16 share, 31 all).
    :type permissions: ``int`` or ``None``
    :param password: Optional password to protect a public-link share.
    :type password: ``str`` or ``None``
    :param public_upload: Allow public upload on a public-link share of a folder.
    :type public_upload: ``bool`` or ``None``
    :param expire_date: Optional expiry date as ``YYYY-MM-DD``.
    :type expire_date: ``str`` or ``None``
    :param share_with: Target user/group/email for non-public shares.
    :type share_with: ``str`` or ``None``
    :return: The share record from ``ocs.data`` (includes ``url`` for public
        links, plus ``id``, ``token`` etc.).
    :rtype: ``dict``
    :raises Exception: If the OCS API reports a failure.

    :Keyword Arguments:
        Any ``nextcloud_*`` connection key accepted by :func:`nextcloud.connect`
        -- only used when ``connection`` is not supplied.

    :Examples:

        Create a public link and return its URL:

            .. code-block:: python

                info = nextcloud.file.share('/jinjamator_test/report.pdf', connection=conn)
                return info['url']

        Share a folder with another user (read/write):

            .. code-block:: python

                nextcloud.file.share('/jinjamator_test', connection=conn,
                                     share_type=0, share_with='someuser', permissions=31)
    """
    conn, auto = _resolve_connection(connection, kwargs)
    try:
        url = f"{conn.ocs_url}/apps/files_sharing/api/v1/shares"
        data = {"path": "/" + str(path).strip("/"), "shareType": int(share_type)}
        if permissions is not None:
            data["permissions"] = int(permissions)
        if password is not None:
            data["password"] = password
        if public_upload is not None:
            data["publicUpload"] = str(bool(public_upload)).lower()
        if expire_date is not None:
            data["expireDate"] = expire_date
        if share_with is not None:
            data["shareWith"] = share_with

        resp = conn.session.post(
            url,
            data=data,
            headers={"OCS-APIRequest": "true", "Accept": "application/json"},
            timeout=conn.timeout,
        )
        try:
            payload = resp.json()
        except ValueError:
            raise Exception(
                f"nextcloud.file.share: unexpected non-JSON response "
                f"(HTTP {resp.status_code}): {resp.text[:200]}"
            )
        meta = payload.get("ocs", {}).get("meta", {})
        # OCS v1 success = 100, v2 success = 200
        if meta.get("statuscode") not in (100, 200):
            raise Exception(
                f"nextcloud.file.share: failed to share '{path}': "
                f"{meta.get('message')} (statuscode {meta.get('statuscode')})"
            )
        sharedata = payload["ocs"]["data"]
        log.debug(
            f"nextcloud.file.share: shared {path} -> {sharedata.get('url', sharedata.get('id'))}"
        )
        return sharedata
    finally:
        if auto:
            ncbackend.disconnect(conn)


def _stat(conn, path):
    """Return ``"dir"``, ``"file"`` or ``None`` for a remote path via PROPFIND.

    A ``Depth: 0`` PROPFIND requesting only ``resourcetype`` is issued; a missing
    resource yields ``None``, a collection ``"dir"`` and anything else ``"file"``.
    """
    url = conn.webdav_path(path)
    body = (
        '<?xml version="1.0"?>'
        '<d:propfind xmlns:d="DAV:"><d:prop><d:resourcetype/></d:prop></d:propfind>'
    )
    resp = conn.session.request(
        "PROPFIND",
        url,
        data=body,
        headers={"Depth": "0", "Content-Type": "application/xml"},
        timeout=conn.timeout,
    )
    if resp.status_code == 404:
        return None
    if resp.status_code != 207:
        raise Exception(
            f"nextcloud.file: PROPFIND '{path}' failed (HTTP {resp.status_code})"
        )
    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError:
        return "file"
    for resourcetype in root.iter("{DAV:}resourcetype"):
        for child in resourcetype:
            if child.tag == "{DAV:}collection":
                return "dir"
    return "file"


def exists(path, connection=None, **kwargs):
    """Check whether a remote path exists.

    :param path: Remote path, relative to the user's files root.
    :type path: ``str``
    :param connection: An existing handle from :func:`nextcloud.connect`. If
        omitted, one is opened from the ``nextcloud_*`` values and closed again.
    :type connection: :class:`NextcloudConnection` or ``None``
    :return: ``True`` if the path exists, ``False`` otherwise.
    :rtype: ``bool``

    :Examples:

        .. code-block:: python

            if nextcloud.file.exists('/jinjamator_test/hello.txt', connection=conn):
                ...
    """
    conn, auto = _resolve_connection(connection, kwargs)
    try:
        return _stat(conn, path) is not None
    finally:
        if auto:
            ncbackend.disconnect(conn)


def is_dir(path, connection=None, **kwargs):
    """Check whether a remote path is a directory (WebDAV collection).

    :param path: Remote path, relative to the user's files root.
    :type path: ``str``
    :param connection: An existing handle from :func:`nextcloud.connect`. If
        omitted, one is opened from the ``nextcloud_*`` values and closed again.
    :type connection: :class:`NextcloudConnection` or ``None``
    :return: ``True`` if the path exists and is a directory, else ``False``.
    :rtype: ``bool``

    :Examples:

        .. code-block:: python

            nextcloud.file.is_dir('/jinjamator_test', connection=conn)
    """
    conn, auto = _resolve_connection(connection, kwargs)
    try:
        return _stat(conn, path) == "dir"
    finally:
        if auto:
            ncbackend.disconnect(conn)


def is_file(path, connection=None, **kwargs):
    """Check whether a remote path is a regular file.

    :param path: Remote path, relative to the user's files root.
    :type path: ``str``
    :param connection: An existing handle from :func:`nextcloud.connect`. If
        omitted, one is opened from the ``nextcloud_*`` values and closed again.
    :type connection: :class:`NextcloudConnection` or ``None``
    :return: ``True`` if the path exists and is a file, else ``False``.
    :rtype: ``bool``

    :Examples:

        .. code-block:: python

            nextcloud.file.is_file('/jinjamator_test/hello.txt', connection=conn)
    """
    conn, auto = _resolve_connection(connection, kwargs)
    try:
        return _stat(conn, path) == "file"
    finally:
        if auto:
            ncbackend.disconnect(conn)


def delete(path, connection=None, **kwargs):
    """Delete a remote file or directory (WebDAV ``DELETE``).

    Deleting a directory removes it recursively (server-side).

    :param path: Remote path to delete, relative to the user's files root.
    :type path: ``str``
    :param connection: An existing handle from :func:`nextcloud.connect`. If
        omitted, one is opened from the ``nextcloud_*`` values and closed again.
    :type connection: :class:`NextcloudConnection` or ``None``
    :return: ``True`` on success.
    :rtype: ``bool``
    :raises Exception: If the path does not exist or could not be deleted.

    :Examples:

        .. code-block:: python

            nextcloud.file.delete('/jinjamator_test/hello.txt', connection=conn)
    """
    conn, auto = _resolve_connection(connection, kwargs)
    try:
        url = conn.webdav_path(path)
        resp = conn.session.request("DELETE", url, timeout=conn.timeout)
        if resp.status_code not in (200, 204):
            raise Exception(
                f"nextcloud.file.delete: failed to delete '{path}' (HTTP {resp.status_code})"
            )
        log.debug(f"nextcloud.file.delete: deleted {path}")
        return True
    finally:
        if auto:
            ncbackend.disconnect(conn)


def move(src, dst, connection=None, overwrite=True, **kwargs):
    """Move or rename a remote file or directory (WebDAV ``MOVE``).

    :param src: Source path, relative to the user's files root.
    :type src: ``str``
    :param dst: Destination path, relative to the user's files root.
    :type dst: ``str``
    :param connection: An existing handle from :func:`nextcloud.connect`. If
        omitted, one is opened from the ``nextcloud_*`` values and closed again.
    :type connection: :class:`NextcloudConnection` or ``None``
    :param overwrite: Overwrite the destination if it exists. Defaults to ``True``.
    :type overwrite: ``bool``
    :return: ``True`` on success.
    :rtype: ``bool``
    :raises Exception: If the move fails.

    :Examples:

        .. code-block:: python

            nextcloud.file.move('/jinjamator_test/hello.txt',
                                '/jinjamator_test/renamed.txt', connection=conn)
    """
    conn, auto = _resolve_connection(connection, kwargs)
    try:
        headers = {
            "Destination": conn.webdav_path(dst),
            "Overwrite": "T" if overwrite else "F",
        }
        resp = conn.session.request(
            "MOVE", conn.webdav_path(src), headers=headers, timeout=conn.timeout
        )
        if resp.status_code not in (201, 204):
            raise Exception(
                f"nextcloud.file.move: failed to move '{src}' -> '{dst}' "
                f"(HTTP {resp.status_code})"
            )
        log.debug(f"nextcloud.file.move: moved {src} -> {dst}")
        return True
    finally:
        if auto:
            ncbackend.disconnect(conn)


def save(data, target_path, connection=None, overwrite=True, create_dirs=True, **kwargs):
    """Save text (or bytes) directly to a remote file -- the upload counterpart of :func:`load`.

    Mirrors ``file.save``: writes ``data`` to ``target_path`` without needing a
    local file on disk.

    :param data: The content to write. ``str`` is sent as UTF-8; ``bytes`` is
        sent verbatim.
    :type data: ``str`` or ``bytes``
    :param target_path: Remote destination path, relative to the user's files root.
    :type target_path: ``str``
    :param connection: An existing handle from :func:`nextcloud.connect`. If
        omitted, one is opened from the ``nextcloud_*`` values and closed again.
    :type connection: :class:`NextcloudConnection` or ``None``
    :param overwrite: Overwrite an existing file. If ``False`` and the target
        exists, nothing is written. Defaults to ``True``.
    :type overwrite: ``bool``
    :param create_dirs: Create the remote parent directory first if missing.
        Defaults to ``True``.
    :type create_dirs: ``bool``
    :return: ``True`` on success, ``False`` if skipped because the target exists
        and ``overwrite`` is ``False``.
    :rtype: ``bool``
    :raises Exception: If the upload fails.

    :Examples:

        .. code-block:: python

            nextcloud.file.save('hello world\\n', '/jinjamator_test/note.txt', connection=conn)
    """
    conn, auto = _resolve_connection(connection, kwargs)
    try:
        if not overwrite and _stat(conn, target_path) is not None:
            log.error(
                f"nextcloud.file.save: {target_path} exists and overwrite is not true"
            )
            return False
        if create_dirs:
            parent_path = parent(target_path)
            if parent_path and parent_path.strip("/"):
                mkdir(parent_path, connection=conn)
        if isinstance(data, str):
            data = data.encode("utf-8")
        resp = conn.session.put(
            conn.webdav_path(target_path), data=data, timeout=conn.timeout
        )
        if resp.status_code not in (200, 201, 204):
            raise Exception(
                f"nextcloud.file.save: failed to write '{target_path}' "
                f"(HTTP {resp.status_code})"
            )
        log.debug(f"nextcloud.file.save: wrote {target_path}")
        return True
    finally:
        if auto:
            ncbackend.disconnect(conn)


def load(path, connection=None, mode="r", **kwargs):
    """Load and return the content of a remote file -- the counterpart of :func:`save`.

    Mirrors ``file.load``: returns the file content as a string (or ``bytes`` in
    binary mode) instead of writing it to disk, and returns ``False`` if the file
    does not exist.

    :param path: Remote source path, relative to the user's files root.
    :type path: ``str``
    :param connection: An existing handle from :func:`nextcloud.connect`. If
        omitted, one is opened from the ``nextcloud_*`` values and closed again.
    :type connection: :class:`NextcloudConnection` or ``None``
    :param mode: ``"r"`` to decode as text (default) or ``"rb"`` for raw bytes.
    :type mode: ``str``
    :return: The file content, or ``False`` if the file does not exist.
    :rtype: ``str`` or ``bytes`` or ``bool``
    :raises Exception: If the download fails for a reason other than "not found".

    :Examples:

        .. code-block:: python

            text = nextcloud.file.load('/jinjamator_test/note.txt', connection=conn)
    """
    conn, auto = _resolve_connection(connection, kwargs)
    try:
        resp = conn.session.get(conn.webdav_path(path), timeout=conn.timeout)
        if resp.status_code == 404:
            log.error(f"nextcloud.file.load: path {path} does not exist")
            return False
        if resp.status_code != 200:
            raise Exception(
                f"nextcloud.file.load: failed to read '{path}' (HTTP {resp.status_code})"
            )
        return resp.content if "b" in mode else resp.text
    finally:
        if auto:
            ncbackend.disconnect(conn)


def open(path, flags="r", connection=None, **kwargs):
    """Open a remote file and return a readable, file-like stream.

    Mirrors ``file.open`` for the http case: returns a streaming descriptor you
    can ``.read()`` from. Only read modes are supported; to write, use
    :func:`save` or :func:`put`.

    :param path: Remote source path, relative to the user's files root.
    :type path: ``str``
    :param flags: Open mode. Only read modes (``"r"`` / ``"rb"``) are supported.
    :type flags: ``str``
    :param connection: An existing handle from :func:`nextcloud.connect`. If
        omitted, one is opened from the ``nextcloud_*`` values. Note: when a
        throwaway connection is used it is intentionally *not* closed here, so
        the returned stream stays usable -- close it yourself when done.
    :type connection: :class:`NextcloudConnection` or ``None``
    :return: A readable, file-like object (the raw HTTP response stream).
    :rtype: ``file``
    :raises NotImplementedError: If a write mode is requested.
    :raises Exception: If the file cannot be opened.

    :Examples:

        .. code-block:: python

            fh = nextcloud.file.open('/jinjamator_test/note.txt', connection=conn)
            data = fh.read()
    """
    if "w" in flags or "a" in flags or "x" in flags or "+" in flags:
        raise NotImplementedError(
            "nextcloud.file.open: write modes are not supported, use nextcloud.file.save() / put()"
        )
    conn, _auto = _resolve_connection(connection, kwargs)
    resp = conn.session.get(conn.webdav_path(path), stream=True, timeout=conn.timeout)
    if resp.status_code != 200:
        raise Exception(
            f"nextcloud.file.open: failed to open '{path}' (HTTP {resp.status_code})"
        )
    resp.raw.decode_content = True
    return resp.raw


def resolve(path, connection=None, **kwargs):
    """Return the full WebDAV URL of a remote path.

    The returned URL is absolute and URL-quoted, e.g.
    ``https://host/remote.php/dav/files/<user-id>/jinjamator_test/hello.txt``.

    :param path: Remote path, relative to the user's files root.
    :type path: ``str``
    :param connection: An existing handle from :func:`nextcloud.connect`. If
        omitted, one is opened from the ``nextcloud_*`` values and closed again.
    :type connection: :class:`NextcloudConnection` or ``None``
    :return: The fully-qualified WebDAV URL of ``path``.
    :rtype: ``str``

    :Examples:

        .. code-block:: python

            url = nextcloud.file.resolve('/jinjamator_test/hello.txt', connection=conn)
    """
    conn, auto = _resolve_connection(connection, kwargs)
    try:
        return conn.webdav_path(path)
    finally:
        if auto:
            ncbackend.disconnect(conn)


def parent(path):
    """Return the parent directory of a remote path (pure string operation).

    No connection is required.

    :param path: Remote path, e.g. ``/jinjamator_test/hello.txt``.
    :type path: ``str``
    :return: The parent directory, e.g. ``/jinjamator_test``.
    :rtype: ``str``

    :Examples:

        .. code-block:: python

            nextcloud.file.parent('/jinjamator_test/hello.txt')   # -> '/jinjamator_test'
    """
    normalized = "/" + str(path).strip("/")
    parent_path = posixpath.dirname(normalized)
    return parent_path if parent_path else "/"


def mkdir_p(path, connection=None, **kwargs):
    """Create a directory and all missing parents (like ``mkdir -p``).

    Convenience wrapper around :func:`mkdir` with ``recursive=True`` -- lazy
    function for lazy ppl, mirroring ``file.mkdir_p``.

    :param path: Remote directory path, relative to the user's files root.
    :type path: ``str``
    :param connection: An existing handle from :func:`nextcloud.connect`. If
        omitted, one is opened from the ``nextcloud_*`` values and closed again.
    :type connection: :class:`NextcloudConnection` or ``None``
    :return: ``True`` on success.
    :rtype: ``bool``

    :Examples:

        .. code-block:: python

            nextcloud.file.mkdir_p('/jinjamator_test/a/b/c', connection=conn)
    """
    return mkdir(path, connection=connection, recursive=True, **kwargs)


def dir(path, pattern="*", connection=None, **kwargs):
    """List the contents of a remote directory (WebDAV ``PROPFIND`` Depth 1).

    Mirrors ``file.dir``: returns the entry *names* by default, or full remote
    paths when called with the ``fullpath`` keyword argument. Entries are
    filtered by ``pattern`` (glob/fnmatch style) and returned sorted. The
    directory itself is not included.

    :param path: Remote directory path, relative to the user's files root.
    :type path: ``str``
    :param pattern: Glob-style name pattern to match, defaults to ``"*"``.
    :type pattern: ``str``
    :param connection: An existing handle from :func:`nextcloud.connect`. If
        omitted, one is opened from the ``nextcloud_*`` values and closed again.
    :type connection: :class:`NextcloudConnection` or ``None``
    :return: Sorted list of entry names, or full remote paths (e.g.
        ``/jinjamator_test/hello.txt``) when ``fullpath`` is passed.
    :rtype: ``list`` of ``str``
    :raises Exception: If the directory does not exist or cannot be listed.

    :Keyword Arguments:
        * *fullpath* -- if present, return full remote paths instead of names.
        * Any ``nextcloud_*`` connection key accepted by :func:`nextcloud.connect`
          -- only used when ``connection`` is not supplied.

    :Examples:

        .. code-block:: python

            nextcloud.file.dir('/jinjamator_test', connection=conn)
            # -> ['hello.txt', 'sub']

            nextcloud.file.dir('/jinjamator_test', '*.txt', connection=conn, fullpath=True)
            # -> ['/jinjamator_test/hello.txt']
    """
    fullpath = "fullpath" in kwargs
    kwargs.pop("fullpath", None)
    conn, auto = _resolve_connection(connection, kwargs)
    try:
        body = (
            '<?xml version="1.0"?>'
            '<d:propfind xmlns:d="DAV:"><d:prop><d:resourcetype/></d:prop></d:propfind>'
        )
        resp = conn.session.request(
            "PROPFIND",
            conn.webdav_path(path),
            data=body,
            headers={"Depth": "1", "Content-Type": "application/xml"},
            timeout=conn.timeout,
        )
        if resp.status_code == 404:
            raise Exception(f"nextcloud.file.dir: directory '{path}' not found")
        if resp.status_code != 207:
            raise Exception(
                f"nextcloud.file.dir: PROPFIND '{path}' failed (HTTP {resp.status_code})"
            )

        dav_prefix = conn.webdav_root[len(conn.base_url):]
        requested = "/" + str(path).strip("/")
        entries = []
        for response in ET.fromstring(resp.content).iter("{DAV:}response"):
            href_el = response.find("{DAV:}href")
            if href_el is None or not href_el.text:
                continue
            href = unquote(href_el.text)
            if href.startswith("http"):  # some servers return absolute hrefs
                href = "/" + href.split("/", 3)[-1]
            remote = href[len(dav_prefix):] if href.startswith(dav_prefix) else href
            remote = "/" + remote.strip("/")
            if remote == requested or remote == "/":
                continue  # skip the directory itself
            name = remote.rstrip("/").split("/")[-1]
            if not fnmatch.fnmatch(name, pattern):
                continue
            entries.append(remote if fullpath else name)
        return sorted(entries)
    finally:
        if auto:
            ncbackend.disconnect(conn)
