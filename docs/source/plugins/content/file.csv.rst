file.csv
===============================================

.. toctree::
    :maxdepth: 1



.. py:function:: file.csv.load(source_path, **kwargs):

    Load data from a CSV file

    :param source_path: URL or local path
    :type source_path: ``str``

    :Keyword Arguments:
        Currently None
    

.. py:function:: file.csv.save(data, destination_path, **kwargs):

    Generate a csv file from a datastructure.

    :param data: Currently data must be a list of dicts.
    :type data: list of dict
    :param destination_path: Path of the resulting CSV file.
    :type destination_path: str
    :raises ValueError: If the format of data cannot be determined.
    :return: Returns True on success.
    :rtype: bool

    :Keyword Arguments:
        Currently None
    


