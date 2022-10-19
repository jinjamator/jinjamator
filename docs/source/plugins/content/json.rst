json
===============================================

.. toctree::
    :maxdepth: 1



.. py:function:: json.dump(data, filepath):

    Write structured json_dump-able data directly to a file

    :param data: structured json_dumps()-able data
    :type data: list,dict
    :param filepath: path to target-file
    :type filpath: string
    :returns: Returns True on success, False on Failure
    :rtype: bool
    

.. py:function:: json.dumps(data):

    Convert structured json_dump-able data into a json-string

    :param data: json_dumps()-able data
    :type data: list,dict
    :returns: json-string
    :rtype: string
    

.. py:function:: json.load(filepath):

    Load json-data directly from a file

    :param filepath: path to source-file
    :type filpath: string
    :returns: structured data
    :rtype: list,dict
    

.. py:function:: json.loads(data):

    Load json-data directly from given string

    :param data: json-string
    :type data: string
    :returns: structured data
    :rtype: list,dict
    


