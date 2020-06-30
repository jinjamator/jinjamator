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
from collections import defaultdict


def tree():
    return defaultdict(tree)


class console(outputPluginBase):
    def addArguments(self):
        self._parent._parser.add_argument(
            "--console-pretty-print",
            dest="console_pretty_print",
            action="count",
            help="use pprint instead of print",
        )

    def connect(self, **kwargs):
        pass

    def process(self, data, **kwargs):
        if not data:
            return True
        if str(data).strip() == "":
            return True
        if self._parent.configuration.get("console_pretty_print"):
            from pprint import pprint

            pprint(data)
        else:
            print(str(data).strip())
        return data

    @staticmethod
    def get_json_schema(configuration={}):
        form = {
            "schema": {
                "type": "object",
                "title": "Output Plugin Parameters",
                "properties": {
                    "console_pretty_print": {
                        "title": "Enable Pretty Print",
                        "type": "boolean",
                        "description": "Shoud the tasklet output be rendered by pretty print function (useful for viewing data structures)",
                    }
                },
            },
            "options": {
                "fields": {
                    "console_pretty_print": {
                        "helper": [
                            "Shoud the tasklet output be rendered by pretty print function (useful for viewing data structures)"
                        ]
                    }
                }
            },
        }

        return dict(form)
