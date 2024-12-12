file.temp
===============================================

.. toctree::
    :maxdepth: 1



.. py:function:: file.temp.dir(**kwargs):

    Create a temporary directory

    :return: tempfile.TemporaryDirectory() object
    :rtype: ``object``
    

.. py:function:: file.temp.file(**kwargs):

    Returns an object for a tempfile
    Currently only the `name` attribute is populated

    :keyword str name: The filename that should be used. Will generate one of none given
    :keyword object,str dir: The temp-dir that should be used to store the file. Can be an existing path (string) or a temp_dir() object
    :return: A `tmpfile` object. Use the `name` attribute to get the filename
    :rtype: ``object``
    

.. py:function:: file.temp.name(temp_obj):

    Gets the name (== the path) of the temp-directory
    Returns False if there is not temp_dir

    :param temp_obj: The temp object (created by temp_dir) from which the name should be extracted
    :type temp_obj: ``object``
    :return: Name of the temp_dir (== the path), False if temp_obj was not a valid object or had no `name` attribute
    :rtype: ``string``, ``bool``
    


