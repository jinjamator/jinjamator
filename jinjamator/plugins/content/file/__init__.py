import os
import logging
import requests

log = logging.getLogger(__name__)
py_open = open


def save(data, target, **kwargs):
    """
    save data to a local file
    """
    mode = kwargs.get("mode", "w")
    if (not os.path.exists(target)) or (
        kwargs.get("overwrite", True) and os.path.isfile(target)
    ):
        with open(target, mode) as fh:
            fh.write(data)
        return True
    log.error(f"Path {target} exists and overwrite is not true or path is a directory")
    return False


def load(path, **kwargs):
    """
    load data from file. local or http/https
    """
    mode = kwargs.get("mode", "r")
    if os.path.isfile(path):
        with open(path, mode) as fh:
            return fh.read()
    log.error(f"Path {path} does not exist")
    return False


def open(url, flags="r"):
    """
    Opens files from local filesystem or http/https and returns a file descriptor
    """

    if url.startswith("http"):
        r = requests.get(url, stream=True, verify=False)
        return r.raw
    else:
        return py_open(url, flags)
