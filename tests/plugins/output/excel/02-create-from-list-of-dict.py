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

data = [
    {"col1": "val1 col1", "col2": "val1 col2"},
    {"col1": "val2 col1", "col2": "val2 col2"},
    {"col1": "val3 col1", "col2": "val3 col2"},
    {"col1": "val4 col1", "col2": "val4 col2"},
    {"col1": "val5 col1", "col2": "val5 col2"},
]

# force excel as output plugin
self.parent.load_output_plugin(
    "excel", self.parent._configuration.get("global_output_plugins_base_dirs")
)

return data
