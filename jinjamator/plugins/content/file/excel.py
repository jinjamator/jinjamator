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
    xlsx.parse_header(kwargs.get("header_lines", 1))
    xlsx.parse_data()
    return xlsx.data


def to_csv(src_path, target_path=None, **kwargs):
    """This function converts an excel file to an CSV file. If the target_path parameter is omitted, it will be constructed from the src_path. Eg. /home/user/test.xlsx -> /home/user/test.csv

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
