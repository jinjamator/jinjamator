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

import yaml as pyyaml


def dumps(data):
    """helper for jinja2"""
    return pyyaml.dump(data)


def loads(data):
    return pyyaml.load(data, Loader=pyyaml.FullLoader)

def dump(data,filepath):
    """
    Write structured yaml_dump-able data directly to a file

    :param data: structured yaml_dumps()-able data
    :type data: list,dict
    :param filepath: path to target-file
    :type filpath: string
    :returns: Returns True on success, False on Failure
    :rtype: bool
    """
    return file.save(dumps(data),filepath)


def load (filepath):
    """
    Load yaml-data directly from a file

    :param filepath: path to source-file
    :type filpath: string
    :returns: structured data
    :rtype: list,dict
    """
    if file.exists(filepath):
        return loads(file.load(filepath))
    else:
        return False

def save (data,filepath):
    """
    Write structured yaml_dump-able data directly to a file
    Alias for yaml.dump() to be consistent with other plugins

    :param data: structured yaml_dumps()-able data
    :type data: list,dict
    :param filepath: path to target-file
    :type filpath: string
    :returns: Returns True on success, False on Failure
    :rtype: bool
    """
    return dump(data,filepath)