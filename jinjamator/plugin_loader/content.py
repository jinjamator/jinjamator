# Copyright 2023 Wilhelm Putz

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
import pathlib
from pprint import pprint
import pkgutil
import types
from inspect import getmembers, isfunction
import pprint
import json


__all_plugins__ = {}
__all_j2_functions__ = {}


def add_builtin(name,code):
    __builtins__[name] = code
    __all_plugins__[name] = code


# always load some functions
add_builtin("pprint",pprint.pprint)
add_builtin("pformat",pprint.pformat)
add_builtin("os",os)
add_builtin("sys",sys)
add_builtin("json",json)


def register_content_plugins(plugin_paths):
    for loader, module_name, is_pkg in pkgutil.walk_packages(plugin_paths):
        _module = loader.find_module(module_name).load_module(module_name)
        if not '.' in module_name:
            __builtins__[module_name] = _module        
        __all_plugins__[module_name]=_module
    for prefix,mod in __all_plugins__.items():
        for name,code in getmembers(mod,isfunction):
            full_name=f"{prefix}.{name}"
            if name.startswith("_"):
                continue
            
            __all_j2_functions__[full_name]=code




__builtins__["all_registered_j2_functions"]=__all_j2_functions__



def j2_load_plugins(env):
        for filter_name, filter in __all_j2_functions__.items():
            if filter_name not in env.filters:
                env.filters[filter_name] = filter
        for function_name, function in __all_plugins__.items():
            if function_name not in env.globals:
                env.globals[function_name] = function
        return env
