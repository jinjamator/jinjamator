import os
import logging
import requests
import pathlib
import shutil
from jinjamator.plugins.content.file import ftp

log = logging.getLogger(__name__)
py_open = open


def save(data, target_path, **kwargs):
    """save text data to a local file

    :param data: Data which should be written to a file
    :type data: str
    :param target_path: path to the new file
    :type target_path: str
    :return: Returns True on success, False on Failure
    :rtype: bool

    :Keyword Arguments:
        * *overwrite* (``bool``) --
          Should a existing file be overwritten?, defaults to True
    """
    mode = kwargs.get("mode", "w")
    if (not os.path.exists(target_path)) or (
        kwargs.get("overwrite", True) and os.path.isfile(target_path)
    ):
        with open(target_path, mode) as fh:
            fh.write(data)
            log.debug(f"successfully written file {target_path}")
        return True
    log.error(
        f"Path {target_path} exists and overwrite is not true or path is a directory"
    )
    return False


def load(path, **kwargs):
    """Load data from a textfile. This function works for local paths an http/https hosted files.

    :param path: Can be a local path or a http/https URL. For relative paths the current task base directory is set as basepath so test.txt will become /path/to/task/test.txt
    :type path: ``str``
    :return: On error opening the File `False` is returned. On success the content of the textfile is returned.
    :rtype: ``bool`` or  ``str``

    :Keyword Arguments:
        None at the moment.
    """
    mode = kwargs.get("mode", "r")
    if not path.startswith("/"):
        path = f"{_jinjamator.task_base_dir}{os.path.sep}{path}"
    if os.path.isfile(path):
        with open(path, mode) as fh:
            return fh.read()
    log.error(f"Path {path} does not exist")
    return False


def open(url, flags="r"):
    """Opens files from local filesystem or http/https/ftp and returns a corresponding descriptor

    :param url: URL
    :type url: ``str``
    :param flags: flags that should be passed to python open see https://docs.python.org/3/library/functions.html#open , defaults to "r"
    :type flags: ``str``, optional
    :return: File descriptor to local file or file served via http/https
    :rtype: ``file``
    """
    """
    
    """
    if url.startswith("http"):
        r = requests.get(url, stream=True, verify=False)
        return r.raw
    if url.startswith("ftp"):
        return ftp.open(url, flags)
    else:
        return py_open(url, flags)


def get_filename(filename):
    """
    Get only the filename
    /some/path/my.file --> my.file

    :param filename: The filename
    :type filename: ``str``
    :return: Filename without path
    :rtype: ``str``
    """
    return pathlib.Path(filename).name


def strip_suffix(filename):
    """
    Strip the suffix from the filename
    /some/path/my.file --> /some/path/my

    :param filename: The filename
    :type filename: ``str``
    :return: Filename without suffix
    :rtype: ``str``
    """
    return pathlib.Path(filename).with_suffix("")


def get_suffix(filename):
    """
    Get the suffix from the filename
    /some/path/my.file --> file

    :param filename: The filename
    :type filename: ``str``
    :return: The suffix
    :rtype: ``str``
    """
    return pathlib.Path(filename).suffix


def change_suffix(filename, suffix=False):
    """
    Change the suffix of the file
    /some/path/my.file --> /some/path/my.othersuffix

    :param filename: The filename
    :type filename: ``str``
    :param suffix: The new suffix (must start with a .). If omitted the suffix will be stripped.
    :type suffix: ``str``
    :return: The filename with the new suffix
    :rtype: ``str``
    """
    return pathlib.Path(filename).with_suffix(suffix)


def is_file(filename):
    """
    Check if filename is a file

    :param filename: The filename
    :type filename: ``str``
    :return: True if it is a file, False if not
    :rtype: ``bool``
    """
    return pathlib.Path(filename).is_file()


def is_dir(filename):
    """
    Check if filename is a directory

    :param filename: The filename
    :type filename: ``str``
    :return: True if it is a directory, False if not
    :rtype: ``bool``
    """
    return pathlib.Path(filename).is_dir()


def exists(filename):
    """
    Check if filename exists

    :param filename: The filename
    :type filename: ``str``
    :return: True if it exists, False if not
    :rtype: ``bool``
    """
    return pathlib.Path(filename).exists()


def resolve(fn=__file__):
    """
    Return the absolute path of the parent directory of the file

    :param fn: The filename. Defaults to __file__
    :type fn: ``str``
    :return: Absolute path of the files directory
    :rtype: ``str``
    """
    source_path = pathlib.Path(fn).resolve()
    source_dir = source_path.parent

    return source_dir


def mkdir(filename, mode=0o777, parents=False, exist_ok=False):
    """
    Create directory

    :param filename: The path of the directory
    :type filename: ``str``
    :param mode: The mode that should be set for the directory
    :type mode: ``int``
    :param parents: If parents is true, any missing parents of this path are created as needed; they are created with the default permissions without taking mode into account (mimicking the POSIX mkdir -p command).
                    If parents is false (the default), a missing parent raises FileNotFoundError.
    :type parents: ``bool``
    :param exist_ok: If exist_ok is true, FileExistsError exceptions will be ignored (same behavior as the POSIX mkdir -p command), but only if the last path component is not an existing non-directory file.
                     If exist_ok is false (the default), FileExistsError is raised if the target directory already exists.
    :type exist_ok: ``bool``
    :return: True if creation was successful
    :rtype: ``bool``
    """
    return pathlib.Path(filename).mkdir(mode, parents, exist_ok)


def mkdir_p(filename):
    """
    Create directory and all parents if the do not exist.
    Will basically do what "mkdir -p" does and uses the mkdir-function in this lib - lazy function for lazy ppl

    :param filename: The path of the directory
    :type filename: ``str``
    :return: True if creation was successful
    :rtype: ``bool``
    """
    return mkdir(filename, parents=True, exist_ok=True)

def rmdir(path,recursive=False):
    """
    Remove a directory. Can be recursive if ``recursive`` parameter is set to True

    :param path: The path of the directory
    :type path: ``str``
    :param recursive: Remove recursive
    :type recursive: ``boolean``
    :return: True if removal was successful
    :rtype: ``bool``
    """
    if recursive:
        return rmdir_r(path)
    else:
        return pathlib.Path(path).rmdir()

def rmdir_r(path):
    """
    Remove a directory recursively. 

    :param path: The path of the directory
    :type path: ``str``
    :return: True if removal was successful
    :rtype: ``bool``
    """
    if not path == "/":
        return shutil.rmtree(path,ignore_errors=True)
    else:
        log.error("Removing the root path is not supported.")
        return False

def dir(path,pattern='',**kwargs):
    content = sorted(pathlib.Path(path).glob(pattern))
    if 'fullpath' in kwargs:
        return [str(d) for d in content]
    else:
        return [str(d.stem) for d in content]

def copy(src, dst, force_overwrite=False, **kwargs):
    if not src.startswith("/"):
        src = f"{_jinjamator.task_base_dir}{os.path.sep}{src}"
    if not dst.startswith("/"):
        dst = f"{_jinjamator.task_base_dir}{os.path.sep}{dst}"

    if exists(dst) and not force_overwrite:
        log.warn(f"skipping existing path {dst}")
        return False

    if not exists(src):
        return False

    src_fh = open(src)
    dst_fh = open(dst, "w")

    while True:
        buffer = src_fh.read(1000000)
        if not buffer:
            break
        dst_fh.write(buffer)
    src_fh.close()
    dst_fh.close()
    return True


def delete(path, recursive=False):
    if not path.startswith("/"):
        path = f"{_jinjamator.task_base_dir}{os.path.sep}{path}"
    os.unlink(path)


def move(src, dst, force_overwrite=False, **kwargs):
    copy(src, dst, force_overwrite, **kwargs)
    delete(src)
