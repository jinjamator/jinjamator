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

import re


def uuid4(value):

    rxg = re.compile(
        r"^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$"
    )
    if not rxg.match(value):
        raise ValueError(f"{value} is not a valid UUID V4 string")
    return value


# # Swagger documentation
uuid4.__schema__ = {
    "type": "string",
    "pattern": r"^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$",
    "description": "UUID V4 string",
}


def task_data(value):
    return value


# task_data.__schema__ = {
#    "type": "object",
#    "additionalProperties": {"$ref": "#/definitions/cisco_nx-os_query"},
# }
