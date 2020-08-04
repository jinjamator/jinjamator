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
import glob
import importlib
import sys
import os
import inspect
from types import ModuleType
import types

global_ldr = None


def import_code(code, name, add_to_sys_modules=False):
    """
    Returns a newly generated module.
    """
    import sys
    import imp

    module = imp.new_module(name)
    module.__file__ = ":inmemory:"

    exec(code, module.__dict__)
    if add_to_sys_modules:
        sys.modules[name] = module

    return module


class contentPlugin(object):
    pass


class ContentPluginLoader(object):
    def __init__(self, parent):
        self._log = logging.getLogger()
        self._filters = {}
        self._functions = {}
        self._parent = parent

    def load(self, base_dir):
        files = glob.glob(
            f"{base_dir}{os.path.sep}**{os.path.sep}*.py", recursive=True
        ) + glob.glob(f"{base_dir}{os.path.sep}*.py")
        for file in files:
            relative_path = file.replace(f"{base_dir}{os.path.sep}", "")
            class_path = (
                relative_path[:-3].replace(os.path.sep, ".").replace(".__init__", "")
            )
            tmp = class_path.split(".")
            key = tmp.pop(0)

            if not self._functions.get(key):
                self._functions[key] = contentPlugin()
            cur = self._functions[key]

            for item in tmp:
                if not hasattr(cur, item):
                    setattr(cur, item, contentPlugin())
                cur = getattr(cur, item)
            code = """
from jinjamator.plugin_loader.content import py_load_plugins
py_load_plugins(globals())
"""
            with open(file, "r") as fh:
                code += fh.read()
            module = import_code(code, class_path)

            # spec = importlib.util.spec_from_file_location(class_path, file)
            # if not spec:
            #     continue
            # else:
            # module = importlib.util.module_from_spec(spec)
            # self._log.info(dir(spec.loader)   )
            # self._log.info(spec.loader)
            # spec.loader.exec_module(module)
            for func_name in dir(module):
                func = getattr(module, func_name)
                if isinstance(func, types.FunctionType):
                    # self._log.debug(f"registering {class_path}.{func_name}")
                    setattr(cur, func_name, func)
                    argspec = inspect.getfullargspec(func)
                    setattr(module, "_jinjamator", self._parent)
                    setattr(module, "__file__", file)
                    if len(argspec.args) == 1:
                        self._filters[f"{class_path}.{func_name}"] = func

    def get_functions(self):
        return self._functions

    def get_filters(self):
        return self._filters


def j2_load_plugins(env, path="plugins/content/*.py"):
    global global_ldr
    if not global_ldr:
        raise Exception("global plugin loader not initialized")
    for filter_name, filter in global_ldr.get_filters().items():
        # global_ldr._log.debug('registred {0}'.format(filter_name))
        env.filters[filter_name] = filter
    for function_name, function in global_ldr.get_functions().items():
        # global_ldr._log.debug('registred {0}'.format(function_name))
        env.globals[function_name] = function
    return env


def py_load_plugins(env, path="plugins/content/*.py"):
    global global_ldr
    if not global_ldr:
        raise Exception("global plugin loader not initialized")
    for function_name, function in global_ldr.get_functions().items():
        # global_ldr._log.debug('registred {0}'.format(function_name))
        env[function_name] = function


def init_loader(parent):
    global global_ldr
    global_ldr = ContentPluginLoader(parent)
    return global_ldr
