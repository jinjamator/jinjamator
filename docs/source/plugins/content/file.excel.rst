file.excel
===============================================

.. toctree::
    :maxdepth: 1



.. py:function:: file.excel.load(path, **kwargs):

        Loads an xlsx file and returns it's content as datastructure.

    :param path: Path to xlsx file eg. /home/user/documents/demo.xlsx
    :type path: ``str``
    :return: a list of ``dict``
    :rtype: list of dict
    
    :Keyword Arguments:
        * *work_sheet_name* (``str``) --
           Name of the worksheet to return data from, defaults to Sheet1 if neither *work_sheet_name* nor *Sheet1* is found the worksheet on index 0 is used.
    

.. py:function:: file.excel.to_csv(src_path, target_path=None, **kwargs):

        This function converts an excel file to an CSV file. If the target_path parameter is omitted, it will be constructed from the src_path. Eg. /home/user/test.xlsx -> /home/user/test.csv

    :param src_path: Path to source excel file which should be converted
    :type src_path: str
    :param target_path: Target path for the converted CSV file, defaults to None
    :type target_path: str, optional
    :return: Returns True on success
    :rtype: boolean
    


