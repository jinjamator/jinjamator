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

import openpyxl
import logging
from pprint import pformat
import xxhash
import json
import glob
import os
import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font
from openpyxl.utils import column_index_from_string, get_column_letter
from openpyxl.utils.cell import coordinate_from_string
from openpyxl.worksheet.table import Table, TableStyleInfo
import xmltodict
from flatten_json import flatten
from natsort import natsorted
from collections import OrderedDict

__version__ = "0.3"
__author__ = "Wilhelm Putz"


class XLSXReader(object):
    """
    returns a dict from an xlsx sheet. Respects ranges.
    """

    def __init__(self, path, worksheet_name, cache=True):
        self.should_cache = cache
        self._log = logging.getLogger("")
        self._path = path
        self._cache = None
        if cache:
            self.calcCacheFileName(path, worksheet_name)
            try:
                staleCacheFiles = glob.glob(
                    "{0}_{1}_*.xlsxcache".format(path, worksheet_name)
                )
                staleCacheFiles.remove(self._cacheFilePath)
                for staleCacheFile in staleCacheFiles:
                    os.remove(staleCacheFile)
                    self._log.info(
                        "removed stale cache file {0}".format(staleCacheFile)
                    )
            except BaseException:
                pass

            try:
                with open(self._cacheFilePath, "r+b") as fh:
                    self.data = json.loads(fh.read())
                    self._log.info("cache for {0} loaded".format(path))
                    self._cache = True

            except BaseException:
                self._cache = None
                self._log.info("no cache for {0} found".format(path))
        if not self._cache:
            self.wb = openpyxl.load_workbook(path, data_only=True)
            try:
                self.ws = self.wb[worksheet_name]
            except KeyError:
                self._log.warn(
                    "sheet {0} not found, using {1}".format(
                        worksheet_name, self.wb.sheetnames[0]
                    )
                )
                self.ws = self.wb[self.wb.sheetnames[0]]
            self.lastRow = self.get_last_row_in_col()

    def datetime_handler(self, x):
        if isinstance(x, datetime.datetime):
            return x.isoformat()
        raise TypeError("Unknown type")

    def calcCacheFileName(self, path, worksheet_name):
        with open(path, "r+b") as fh:
            digest = xxhash.xxh64(fh.read()).hexdigest()
        self._log.debug("got digest:{0}".format(digest))
        self._cacheFilePath = "{0}_{1}_{2}.xlsxcache".format(
            path, worksheet_name, digest
        )
        self._log.debug("got cache filename:{0}".format(digest))

    def parse_header(self, header_lines=1):
        if self._cache:
            return None
        self.header_fields = []
        if header_lines > 0:
            self._dataOffset = header_lines
        else:
            self._dataOffset = 0
        self._log.debug("detected data offset: {0}".format(self._dataOffset))

        self.merged_cells = {}
        for _range in self.ws.merged_cell_ranges:
            self.merged_cells[str(_range)] = list(
                openpyxl.utils.rows_from_range(str(_range))
            )
        self._log.debug(
            "created merged cell ranges lookup table: {0}".format(self._dataOffset)
        )

        for row_index in range(1, header_lines + 1):
            for cell in self.ws[row_index]:
                try:
                    self.header_fields[cell.column - 1].append(
                        self.get_value_with_merge_lookup(cell)
                    )
                except IndexError:
                    self.header_fields.append([])
                    self.header_fields[cell.column - 1].append(
                        self.get_value_with_merge_lookup(cell)
                    )
        self.header = [" ".join(f).strip() for f in self.header_fields]
        self._log.debug("finished parsing of header")

    def get_last_row_in_col(self, col="A"):
        lastRow = self.ws.max_row

        while self.ws.cell(column=1, row=lastRow).value is None and lastRow > 0:
            lastRow -= 1
        self._log.debug("detected lastRowIn: {0}".format(lastRow))
        return lastRow

    def get_header_for_col(self, col):
        return self.header[col - 1]

    def parse_data(self):
        if self._cache:
            return None
        self._log.info("parsing file: {0}".format(self._path))
        self.data = {}

        for row_index in range(1 + self._dataOffset, self.lastRow + 1):
            self._log.debug("processing row {0}".format(row_index))
            assocRow = {}
            for cell in self.ws[row_index]:
                assocRow[
                    self.get_header_for_col(cell.column)
                ] = self.get_value_with_merge_lookup(cell)
            self.data[row_index] = assocRow
        self._log.info("finished parsing file: {0}".format(self._path))
        self._log.debug(pformat(self.data))
        if self.should_cache:
            self._log.info(
                "saving cachefile to speedup next run: {0}".format(self._cacheFilePath)
            )
            with open(self._cacheFilePath, "w") as fh:
                fh.write(json.dumps(self.data, default=self.datetime_handler))

    def get_value_with_merge_lookup(self, cell):
        for _range, merged_cells in self.merged_cells.items():
            for row in merged_cells:
                if cell.coordinate in row:
                    if not self.ws[merged_cells[0][0]].value:
                        return ""
                    return self.ws[merged_cells[0][0]].value
        if not cell.value:
            return ""
        return cell.value

    def get_worksheets(self):
        return self.wb.sheetnames


class XLSXWriter(object):
    def __init__(self, path, **kwargs):
        self._log = logging.getLogger()
        self._data = None
        self._order_header = False
        self._header = []
        self._append_sheet = kwargs.get("append_sheet") or False
        self._overwrite_file = kwargs.get("overwrite") or False
        self._destintaion_path = path
        self._freeze_panes = kwargs.get("freeze_pane_cell") or "B1"
        self._column_order = kwargs.get("column_order") or False
        self._rename_columns = kwargs.get("rename_columns") or []
        self._table_style_name = "TableStyleMedium15"
        self._table_name = "Table1"
        self._text_wrap = kwargs.get("text_wrap") or True

        if os.path.isfile(self._destintaion_path) and self._append_sheet:
            self._log.info(f"appending to {self._destintaion_path}")
            self._wb = load_workbook(self._destintaion_path)
        elif os.path.isfile(self._destintaion_path) and self._overwrite_file:
            self._log.info(f"overwriting {self._destintaion_path}")
            self._wb = Workbook()
        elif not os.path.isfile(self._destintaion_path):
            self._log.info(f"creating {self._destintaion_path}")
            self._wb = Workbook()
        else:
            raise ValueError(
                f"destination path {self._destintaion_path} already exists and neither append, nor overwrite specified"
            )

    def sanitize_data(self):
        data = self._data

        if isinstance(data, str):
            try:
                self._data = json.loads(self._data)
            except ValueError:
                pass
            except TypeError:
                pass
            try:
                self._data = xmltodict.parse(self._data)
            except ValueError:
                pass
            except TypeError:
                pass

        if isinstance(self._data, dict):
            self._header = list(data.keys())
            is_pseudo_list = True
            for field in self._header:
                try:
                    int(field)
                except ValueError:
                    is_pseudo_list = False
            if is_pseudo_list:  # convert to real list
                self._data = list(self._data.values())
            else:
                self._data = flatten(self._data)
                self._header = list(self._data.keys())

        if isinstance(self._data, list):
            for index, line in enumerate(self._data):
                data_type = "list_of_dict"
                if isinstance(line, list):
                    data_type = "list_of_list"
                    pass
                elif isinstance(line, dict):
                    self._data[index] = flatten(line)
                else:
                    raise ValueError(
                        f"Line {index} is neither, list nor dict. I don't know how to proceed further {line}"
                    )
            if data_type == "list_of_dict":
                self._header = list(self._data[0].keys())
            else:
                self._header = [
                    f"column {counter}"
                    for counter in range(1, len(self._data[index]) + 1)
                ]

        if self._order_header:
            self._header = natsorted(self._header)

        if self._column_order:
            for row in self._data:
                new_row = OrderedDict()
                for column in self._column_order:
                    try:
                        new_row[column] = row[column]
                    except KeyError:
                        new_row[column] = ""

                data.append(new_row)
            self._header = self._column_order

        for old, new in self._rename_columns:
            for i, val in enumerate(self._header):
                if val == old:
                    self._header[i] = new

    def optimize_column_widths(self, ws):
        column_widths = []

        for row in ws.iter_rows():
            for i, cell in enumerate(row):
                if self._text_wrap:
                    cell.alignment = Alignment(
                        horizontal="left", vertical="top", wrapText=True
                    )
                try:
                    if (
                        self._text_wrap
                        and isinstance(cell.value, str)
                        and "\n" in cell.value
                    ):
                        length = 0
                        tmp = cell.value.split("\n")
                        for j in tmp:
                            l = len(j)
                            if l > length:
                                length = l
                    else:
                        length = len(cell.value)
                except TypeError:
                    length = 0
                if len(column_widths) > i:
                    if length > column_widths[i]:
                        column_widths[i] = length
                else:
                    column_widths += [length]

        for i, column_width in enumerate(column_widths):
            ws.column_dimensions[get_column_letter(i + 1)].width = column_width + 4

    def save(self):
        self._wb.save(self._destintaion_path)

    def create_sheet_from_data(self, data, sheet_name):
        self._data = data
        self.sanitize_data()

        if self._append_sheet:
            try:
                ws = self._wb[sheet_name[:30]]

            except BaseException:
                ws = self._wb.create_sheet(title=sheet_name[:30], index=0)
                ws.append(self._header)
        else:
            ws = self._wb.create_sheet(title=sheet_name[:30], index=0)
            ws.append(self._header)
        for row in data:
            values = (row.get(k, "") for k in self._header)
            ws.append(values)

        tab = Table(
            displayName=sheet_name[:30].replace(" ", "_"),
            ref=f"A1:{get_column_letter(ws.max_column)}{ws.max_row}",
        )

        # Add a default style with striped rows and banded columns
        style = TableStyleInfo(
            name=self._table_style_name,
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=True,
        )
        tab.tableStyleInfo = style

        ws.add_table(tab)

        ws.freeze_panes = self._freeze_panes
        self.optimize_column_widths(ws)

        return ws


if __name__ == "__main__":
    pass
