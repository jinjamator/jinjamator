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

import sys
import os
from jinjamator.tools.output_plugin_base import outputPluginBase
import os
import json
import errno
import json
import xmltodict
import tempfile
from flatten_json import flatten
from natsort import natsorted
from jinjamator.tools.xlsx_tools import XLSXWriter


class excel(outputPluginBase):
    def addArguments(self):
        self._parent._parser.add_argument(
            "--excel-output-file-prefix",
            dest="output_filename_prefix",
            help="destination file name prefix [default: %(default)s]",
            default="",
        )
        self._parent._parser.add_argument(
            "--excel-output-directory",
            dest="output_directory",
            help="destination directory for generated files",
            default="./",
        )
        self._parent._parser.add_argument(
            "--excel-sheet-name",
            dest="sheet_name",
            help="set excel sheet name[default: %(default)s]",
            default="sheet 1",
        )
        self._parent._parser.add_argument(
            "--excel-order-header",
            dest="order_header",
            help="lexically order header fields [default: %(default)s]",
            default=False,
            action="store_false",
        )
        self._parent._parser.add_argument(
            "--excel-freeze-pane",
            dest="freeze_pane_cell",
            help="set excel freeze pane to cell [default: %(default)s]",
            metavar="<Excel cell name>",
            default="B2",
        )

        self._parent._parser.add_argument(
            "--excel-rename-column",
            dest="rename_columns",
            default=[],
            action="append",
            help="Rename a data colum. Format: <original_name>:<new_name> [default: %(default)s]",
        )

        self._parent._parser.add_argument(
            "--excel-set-columns",
            dest="columns",
            help="Set columns. Format: <col_name_1>:<col_name_2>:<col_name_n> [default: %(default)s]",
        )

    def connect(self, **kwargs):
        pass

    def process(self, data, **kwargs):
        if isinstance(data, list) or isinstance(data, str):
            if len(data) == 0:
                self._log.warning("refusing to generate excel file from empty data")
                return False
        elif isinstance(data, dict):
            if len(list(data.keys())) == 0:
                self._log.warning("refusing to generate excel file from empty data")
                return False

        if self._parent._configuration.get("task_run_mode") == "background":
            self._parent.configuration["output_directory"] = os.path.join(
                self._parent._configuration.get(
                    "jinjamator_user_directory", tempfile.gettempdir()
                ),
                "logs",
                self._parent._configuration.get("jinjamator_job_id"),
                "files",
            )

        try:
            os.makedirs(
                self._parent.configuration.get("output_directory", "./"), exist_ok=True
            )
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
            pass

        file_name = kwargs["template_path"]
        for directory in self._parent._configuration.get("global_tasks_base_dirs"):
            file_name = file_name.replace(directory, "")
        if file_name[0] == os.path.sep:
            file_name = file_name[1:]

        dest = "{0}/{1}{2}.xlsx".format(
            self._parent.configuration.get("output_directory", "./"),
            self._parent.configuration.get("output_filename_prefix", ""),
            file_name.replace(os.path.sep, "_"),
        )

        if self._parent.configuration.get("columns"):
            column_order = self._parent.configuration.get("columns").split(":")
        else:
            column_order = False

        rename_columns = []

        for rename in self._parent.configuration.get("rename_columns", []):
            tmp = rename.split(":")
            old = tmp.pop(0)
            new = ":".join(tmp)
            rename_columns.append((old, new))

        writer = XLSXWriter(
            dest,
            overwrite=True,
            append_sheet=False,
            column_order=column_order,
            rename_columns=rename_columns,
        )

        writer.create_sheet_from_data(
            data, self._parent.configuration.get("sheet_name", "sheet 1")
        )
        writer.save()
        self._log.info("sucessfully written file: {0}".format(dest))
