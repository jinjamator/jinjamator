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
from json import dumps


class json(outputPluginBase):
    def addArguments(self):
        self._parent._parser.add_argument(
            "-jc",
            "--json-color",
            dest="json_color",
            action="count",
            help="colorize json output",
        )

    def connect(self, **kwargs):
        self.json_color=False
        if self._parent.configuration.get("json_color"):
            self.json_color = True
        

    def process(self, data, **kwargs):
        

        retval="{}"
        try:
            retval=dumps(data, sort_keys=True, indent=2)
        except  TypeError:
            retval=dumps(data, sort_keys=False, indent=2)
        if self.json_color:
            try:
                from pygments import highlight, lexers, formatters
            except ImportError:
                self._parent._log.error("cannot import pygments (run pip install pygments to install), no colorization possible")
                print(retval.strip())
                return retval
            if self._parent._configuration.get("task_run_mode","interactive") == "interactive":
                formatter=formatters.TerminalFormatter()
            print(highlight(retval, lexers.JsonLexer(), formatter).strip())
            return retval
        print(retval.strip())
        return retval

