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
    

.. py:function:: json.dumps(data, color=False):

    Convert structured json_dump-able data into a json-string

    :param data: json_dumps()-able data
    :type data: list,dict
    :param color: Use pygments to highlight json data
    :type color: boolean
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
    

.. py:function:: json.save(data, filepath):

    Write structured json_dump-able data directly to a file
    Alias for json.dump() to be consistent with other plugins

    :param data: structured json_dumps()-able data
    :type data: list,dict
    :param filepath: path to target-file
    :type filpath: string
    :returns: Returns True on success, False on Failure
    :rtype: bool
    


