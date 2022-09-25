device
===============================================

.. toctree::
    :maxdepth: 1

    device.cisco.rst
    device.switch.rst


.. py:function:: device.change_suffix(filename, suffix=False):

    Change the suffix of the file
    /some/path/my.file --> /some/path/my.othersuffix

    :param filename: The filename
    :type filename: ``str``
    :param suffix: The new suffix (must start with a .). If omitted the suffix will be stripped.
    :type suffix: ``str``
    :return: The filename with the new suffix
    :rtype: ``str``
    

.. py:function:: device.compile_instructions(dev_dict, key):

    not documented yet

.. py:function:: device.exists(filename):

    Check if filename exists

    :param filename: The filename
    :type filename: ``str``
    :return: True if it exists, False if not
    :rtype: ``bool``
    

.. py:function:: device.get_filename(filename):

    Get only the filename
    /some/path/my.file --> my.file

    :param filename: The filename
    :type filename: ``str``
    :return: Filename without path
    :rtype: ``str``
    

.. py:function:: device.get_suffix(filename):

    Get the suffix from the filename
    /some/path/my.file --> file

    :param filename: The filename
    :type filename: ``str``
    :return: The suffix
    :rtype: ``str``
    

.. py:function:: device.is_dir(filename):

    Check if filename is a directory

    :param filename: The filename
    :type filename: ``str``
    :return: True if it is a directory, False if not
    :rtype: ``bool``
    

.. py:function:: device.is_file(filename):

    Check if filename is a file

    :param filename: The filename
    :type filename: ``str``
    :return: True if it is a file, False if not
    :rtype: ``bool``
    

.. py:function:: device.load(path, **kwargs):

    Load data from a textfile. This function works for local paths an http/https hosted files.

    :param path: Can be a local path or a http/https URL. For relative paths the current task base directory is set as basepath so test.txt will become /path/to/task/test.txt
    :type path: ``str``
    :return: On error opening the File `False` is returned. On success the content of the textfile is returned. 
    :rtype: ``bool`` or  ``str``

    :Keyword Arguments:
        None at the moment.
    

.. py:function:: device.new():

    not documented yet

.. py:function:: device.open(url, flags='r'):

    Opens files from local filesystem or http/https/ftp and returns a corresponding descriptor

    :param url: URL
    :type url: ``str``
    :param flags: flags that should be passed to python open see https://docs.python.org/3/library/functions.html#open , defaults to "r"
    :type flags: ``str``, optional
    :return: File descriptor to local file or file served via http/https
    :rtype: ``file``
    

.. py:function:: device.save(data, target_path, **kwargs):

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
    

.. py:function:: device.strip_suffix(filename):

    Strip the suffix from the filename
    /some/path/my.file --> /some/path/my

    :param filename: The filename
    :type filename: ``str``
    :return: Filename without suffix
    :rtype: ``str``
    


