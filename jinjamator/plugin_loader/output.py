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

import importlib


def load_output_plugin(obj, output_plugin, search_paths):
    """ 
    Loads an jinjamator output plugin and registers it
    """

    for path in search_paths:
        try:
            spec = importlib.util.spec_from_file_location(
                output_plugin, f"{path}/{output_plugin}/__init__.py"
            )
            if not spec:
                continue
            else:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                obj._output_plugin = getattr(module, output_plugin)(obj)
        except FileNotFoundError:
            obj._log.debug(
                f"cannot find plugin {output_plugin} in path {path}/{output_plugin}/__init__.py"
            )
            pass
