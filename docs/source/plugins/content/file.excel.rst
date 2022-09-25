file.excel
===============================================

.. toctree::
    :maxdepth: 1



.. py:function:: file.excel.get_worksheets(path, **kwargs):

    Gets all available worksheets within a xlsx-file and returns a list
    
    :param path: Path to excel file 
    :type path: str
    :return: Returns a list with all worksheets within the excel-file
    :rtype: list
    

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

    This function converts an excel file to a CSV file. If the target_path parameter is omitted, it will be constructed from the src_path. Eg. /home/user/test.xlsx -> /home/user/test.csv

    :param src_path: Path to source excel file which should be converted
    :type src_path: str
    :param target_path: Target path for the converted CSV file, defaults to None
    :type target_path: str, optional
    :return: Returns True on success
    :rtype: boolean
    

.. py:function:: file.excel.to_csv_ws(src_path, target_path=None, **kwargs):

    This function converts an excel file to a CSV file creating a file for each worksheet. If the target_path parameter is omitted, it will be constructed from the src_path. Eg. /home/user/test.xlsx -> /home/user/test.csv

    :param src_path: Path to source excel file which should be converted
    :type src_path: str
    :param target_path: Target path for the converted CSV file, defaults to None
    :type target_path: str, optional
    :Keyword Arguments:
        * *ws_separator* (``str``) --
           String which shall be used to separate the filename from the worksheet. Default: __
           file.xlsx --> file__worksheet.csv
        * *ws_names* (``list``) --
           List of worksheets that should be converted to CSV. If not defined all worksheets will be converted. If worksheet does not exist an error will be logged, the return-value will not be changed
    :return: Returns True on success
    :rtype: boolean
    


