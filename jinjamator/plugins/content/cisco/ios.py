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

# from jinjamator.plugin_loader.content import py_load_plugins


def query(command, connection=None, **kwargs):
    # py_load_plugins(globals())
    kwargs["device_type"] = "cisco_ios"
    return ssh.query(command, connection, **kwargs)
