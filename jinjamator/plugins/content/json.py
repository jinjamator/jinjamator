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

from json import dumps as json_dumps, loads as json_loads


def dumps(data):
    """
    Convert structured json_dump-able data into a json-string

    :param data: json_dumps()-able data
    :type data: list,dict
    :returns: json-string
    :rtype: string
    """
    return json_dumps(data, sort_keys=True, indent=2)

def dump(data,filepath):
    """
    Write structured json_dump-able data directly to a file

    :param data: structured json_dumps()-able data
    :type data: list,dict
    :param filepath: path to target-file
    :type filpath: string
    :returns: Returns True on success, False on Failure
    :rtype: bool
    """
    return file.save(dumps(data),filepath)

def loads(data):
    """
    Load json-data directly from given string

    :param data: json-string
    :type data: string
    :returns: structured data
    :rtype: list,dict
    """
    return json_loads(data)

def load (filepath):
    """
    Load json-data directly from a file

    :param filepath: path to source-file
    :type filpath: string
    :returns: structured data
    :rtype: list,dict
    """
    if file.exists(filepath):
        return json.loads(file.load(filepath))
    else:
        return False