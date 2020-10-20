file
===============================================

.. toctree::
    :maxdepth: 1

    file.csv.rst
    file.excel.rst


.. py:function:: file.load(path, **kwargs):

    Load data from a textfile. This function works for local paths an http/https hosted files.

    :param path: Can be a local path or a http/https URL. For relative paths the current task base directory is set as basepath so test.txt will become /path/to/task/test.txt
    :type path: ``str``
    :return: On error opening the File `False` is returned
    :rtype: ``bool``
    :return: On success the content of the textfile is returned. 
    :rtype: ``str``

    :Keyword Arguments:
        None at the moment.
    

.. py:function:: file.open(url, flags='r'):

    Opens files from local filesystem or http/https and returns a corresponding descriptor

    :param url: URL
    :type url: ``str``
    :param flags: flags that should be passed to python open see https://docs.python.org/3/library/functions.html#open , defaults to "r"
    :type flags: ``str``, optional
    :return: File descriptor to local file or file served via http/https
    :rtype: ``file``
    

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
    


