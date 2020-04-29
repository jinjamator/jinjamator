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

import logging


class notImplemented(Exception):
    pass


class processError(Exception):
    pass


class outputPluginBase(object):
    def __init__(self, parent):
        self._log = logging.getLogger()
        self._parent = parent

    def addArguments(self):
        raise notImplemented

    def init_plugin_params(self, **kwargs):
        pass

    def connect(self, **kwargs):
        raise notImplemented

    def process(self, data, **kwargs):
        raise notImplemented

    @staticmethod
    def get_json_schema(configuration={}):
        form = {
            "schema": {"type": "object", "properties": {}},
            "options": {"fields": {}},
        }

        return form
