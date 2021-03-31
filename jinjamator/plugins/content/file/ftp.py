from ftplib import FTP
from urllib.parse import urlparse
import io
import logging

log = logging.getLogger()


def login(url):
    parsed_url = urlparse(url)
    username = "anonymous"
    password = ""
    if parsed_url.username:
        username = parsed_url.username
    if parsed_url.password:
        password = parsed_url.password
    ftp = FTP(parsed_url.hostname)

    if not ftp.login(username, password).startswith("230"):
        raise ValueError("invalid username or password")
    else:
        log.debug("Logged in successfully")
    return ftp


def open(url, flags="rp"):
    ftp = login(url)

    if "p" in flags:
        ftp.set_pasv(True)
    if "r" in flags:
        if "b" in flags:
            fp = io.BytesIO()
            result = ftp.retrbinary(f"RETR {parsed_url.path}", fp.write)
        else:
            fp = io.StringIO()
            result = ftp.retrlines(f"RETR {parsed_url.path}", fp.write).startswith(
                "226"
            )
        if result:
            log.debug(f"successfully transferred file {parsed_url.path}")
        fp.seek(0)
    if "w" in flags:
        raise NotImplementedError("FTP upload not yet implemented")
    if "d" in flags:
        ftp.delete(parsed_url.path)
    ftp.close()
    return fp
