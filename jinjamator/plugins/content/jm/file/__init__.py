import requests


def open(url, flags="r"):
    """
    Opens files from local filesystem or http/https and returns a file descriptor
    """

    if url.startswith("http"):
        r = requests.get(url, stream=True, verify=False)
        return r.raw
    else:
        return open(path, flags)


def read(url):
    """
    Returns the content of files from local filesystem or http/https
    """
    with open(url) as fh:
        return fh.read()
