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
    if not os.path.isabs(path):
        path = os.path.join(_jinjamator.task_base_dir, path)
    xlsx = XLSXReader(
        path, kwargs.get("work_sheet_name", "Sheet1"), kwargs.get("cache", True)
    )
    xlsx.parse_header(kwargs.get("header_lines", 1))
    xlsx.parse_data()
    return xlsx.data
