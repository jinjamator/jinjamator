file.excel
===============================================

.. toctree::
    :maxdepth: 1


Module contents
---------------

.. py:function:: file.excel.load(path, **kwargs):

        not documented yet

.. py:function:: file.excel.to_csv(src_path, target_path=None, **kwargs):

        This function converts an excel file to an CSV file. If the target_path parameter
    is omitted, it will be constructed from the src_path. Eg. /home/user/test.xlsx -> /home/user/test.csv

    :param src_path: Path to source excel file which should be converted
    :type src_path: str
    :param target_path: Target path for the converted CSV file, defaults to None
    :type target_path: str, optional
    :return: Returns True on success
    :rtype: boolean
    



