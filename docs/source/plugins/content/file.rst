file
===============================================

.. toctree::
    :maxdepth: 1

    file.csv.rst
    file.excel.rst
    file.ftp.rst


.. py:function:: file.change_suffix(filename, suffix=False):

    Change the suffix of the file
    /some/path/my.file --> /some/path/my.othersuffix

    :param filename: The filename
    :type filename: ``str``
    :param suffix: The new suffix (must start with a .). If omitted the suffix will be stripped.
    :type suffix: ``str``
    :return: The filename with the new suffix
    :rtype: ``str``
    

.. py:function:: file.copy(src, dst, force_overwrite=False, **kwargs):

    not documented yet

.. py:function:: file.delete(path, recursive=False):

    not documented yet

.. py:function:: file.dir(path, pattern='', **kwargs):

    not documented yet

.. py:function:: file.exists(filename):

    Check if filename exists

    :param filename: The filename
    :type filename: ``str``
    :return: True if it exists, False if not
    :rtype: ``bool``
    

.. py:function:: file.get_filename(filename):

    Get only the filename
    /some/path/my.file --> my.file

    :param filename: The filename
    :type filename: ``str``
    :return: Filename without path
    :rtype: ``str``
    

.. py:function:: file.get_suffix(filename):

    Get the suffix from the filename
    /some/path/my.file --> file

    :param filename: The filename
    :type filename: ``str``
    :return: The suffix
    :rtype: ``str``
    

.. py:function:: file.is_dir(filename):

    Check if filename is a directory

    :param filename: The filename
    :type filename: ``str``
    :return: True if it is a directory, False if not
    :rtype: ``bool``
    

.. py:function:: file.is_file(filename):

    Check if filename is a file

    :param filename: The filename
    :type filename: ``str``
    :return: True if it is a file, False if not
    :rtype: ``bool``
    

.. py:function:: file.load(path, **kwargs):

    Load data from a textfile. This function works for local paths an http/https hosted files.

    :param path: Can be a local path or a http/https URL. For relative paths the current task base directory is set as basepath so test.txt will become /path/to/task/test.txt
    :type path: ``str``
    :return: On error opening the File `False` is returned. On success the content of the textfile is returned.
    :rtype: ``bool`` or  ``str``

    :Keyword Arguments:
        None at the moment.
    

.. py:function:: file.mkdir(filename, mode=511, parents=False, exist_ok=False):

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
    

.. py:function:: file.mkdir_p(filename):

    Create directory and all parents if the do not exist.
    Will basically do what "mkdir -p" does and uses the mkdir-function in this lib - lazy function for lazy ppl

    :param filename: The path of the directory
    :type filename: ``str``
    :return: True if creation was successful
    :rtype: ``bool``
    

.. py:function:: file.move(src, dst, force_overwrite=False, **kwargs):

    not documented yet

.. py:function:: file.open(url, flags='r'):

    Opens files from local filesystem or http/https/ftp and returns a corresponding descriptor

    :param url: URL
    :type url: ``str``
    :param flags: flags that should be passed to python open see https://docs.python.org/3/library/functions.html#open , defaults to "r"
    :type flags: ``str``, optional
    :return: File descriptor to local file or file served via http/https
    :rtype: ``file``
    

.. py:function:: file.resolve(fn=':inmemory:'):

    Return the absolute path of the parent directory of the file

    :param fn: The filename. Defaults to __file__
    :type fn: ``str``
    :return: Absolute path of the files directory
    :rtype: ``str``
    

.. py:function:: file.rmdir(path, recursive=False):

    Remove a directory. Can be recursive if ``recursive`` parameter is set to True

    :param path: The path of the directory
    :type path: ``str``
    :param recursive: Remove recursive
    :type recursive: ``boolean``
    :return: True if removal was successful
    :rtype: ``bool``
    

.. py:function:: file.rmdir_r(path):

    Remove a directory recursively. 

    :param path: The path of the directory
    :type path: ``str``
    :return: True if removal was successful
    :rtype: ``bool``
    

.. py:function:: file.save(data, target_path, **kwargs):

    save text data to a local file

    :param data: Data which should be written to a file
    :type data: str
    :param target_path: path to the new file
    :type target_path: str
    :return: Returns True on success, False on Failure
    :rtype: bool

    :Keyword Arguments:
        * *overwrite* (``bool``) --
          Should a existing file be overwritten?, defaults to True
    

.. py:function:: file.strip_suffix(filename):

    Strip the suffix from the filename
    /some/path/my.file --> /some/path/my

    :param filename: The filename
    :type filename: ``str``
    :return: Filename without suffix
    :rtype: ``str``
    


