# Copyright 2019 Wilhelm Putz

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from jinjamator.tools.xlsx_tools import XLSXReader, XLSXWriter
import os
import logging

log = logging.getLogger()


def load(path, **kwargs):
    """Loads an xlsx file and returns it's content as datastructure.

    :param path: Path to xlsx file eg. /home/user/documents/demo.xlsx
    :type path: ``str``
    :return: a list of ``dict``
    :rtype: list of dict

    :Keyword Arguments:
        * *work_sheet_name* (``str``) --
           Name of the worksheet to return data from, defaults to Sheet1 if neither *work_sheet_name* nor *Sheet1* is found the worksheet on index 0 is used.
    """
    if not os.path.isabs(path):
        path = os.path.join(_jinjamator.task_base_dir, path)
    xlsx = XLSXReader(
        path, kwargs.get("work_sheet_name", "Sheet1"), kwargs.get("cache", True)
    )
    if kwargs.get("all_sheets") == True:
        del kwargs["all_sheets"]
        retval={}
        log.debug(f"loading all sheets {xlsx.get_worksheets()} from {path}")
        for ws_name in xlsx.get_worksheets():
            retval["ws_name"]=load(path,work_sheet_name=ws_name,**kwargs)
        return retval
    
    xlsx.parse_header(kwargs.get("header_lines", 1))
    xlsx.parse_data()
    return xlsx.data



def save(data, destination_path, **kwargs):
    """Generate a xlsx file from a datastructure. Currently just a single sheet is supported

    :param data: Currently data must be a list of dicts.
    :type data: list of dict
    :param destination_path: Path of the resulting CSV file.
    :type destination_path: str
    :raises ValueError: If the format of data cannot be determined.
    :return: Returns True on success.
    :rtype: bool

    :Keyword Arguments:
        Currently None
    """
    if isinstance(data,dict):
        data = convert_dict(data)
    
    if isinstance(data, list):
        if isinstance(data[0], dict):
            xlsx = XLSXWriter(destination_path, overwrite=True,**kwargs)
            xlsx.create_sheet_from_data(data, kwargs.get("sheet_name", "Sheet1"))
            xlsx.save()
            log.debug(
                f"successfully written {len(data)} lines of data to {destination_path}"
            )
            return True
        raise ValueError(f"xlsx save not implemented for list of {type(data[0])}")
    raise ValueError(f"xlsx save not implemented for {type(data)}")


def to_csv(src_path, target_path=None, **kwargs):
    """This function converts an excel file to a CSV file. If the target_path parameter is omitted, it will be constructed from the src_path. Eg. /home/user/test.xlsx -> /home/user/test.csv

    :param src_path: Path to source excel file which should be converted
    :type src_path: str
    :param target_path: Target path for the converted CSV file, defaults to None
    :type target_path: str, optional
    :return: Returns True on success
    :rtype: boolean
    """

    data = [v for k, v in load(src_path, cache=False).items()]
    file.csv.save(data, target_path)
    return True


def get_worksheets(path, **kwargs):
    """
    Gets all available worksheets within a xlsx-file and returns a list

    :param path: Path to excel file
    :type path: str
    :return: Returns a list with all worksheets within the excel-file
    :rtype: list
    """
    if not os.path.isabs(path):
        path = os.path.join(_jinjamator.task_base_dir, path)
    xlsx = XLSXReader(path, "Sheet1", kwargs.get("cache", True))
    return xlsx.get_worksheets()


def to_csv_ws(src_path, target_path=None, **kwargs):
    """
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
    """
    fn_ws_sep = kwargs.get("ws_separator", "__")
    ws_list = kwargs.get("ws_names", list())
    all_ws = get_worksheets(src_path)
    if len(ws_list) == 0:
        ws_list = all_ws

    for ws in ws_list:
        if ws in all_ws:
            data = [
                v for k, v in load(src_path, cache=False, work_sheet_name=ws).items()
            ]
            tfn = f"{file.strip_suffix(target_path)}{fn_ws_sep}{ws}.{file.get_suffix(target_path)}"
            log.debug(f"Saving csv to {tfn}")
            file.csv.save(data, tfn)
        else:
            log.error(f"Cant save CSV, worksheet {ws} does not exist")

    return True


def convert_dict (d):
    """
    Convert a dictionary to a list that can be written to excel

    :param d: Dictionary which should be converted
    :type src_path: dict
    :return: List with the dict values
    :rtype: list
    """
    rows = []

    for v in d.values():
        rows.append(v)
    
    return rows