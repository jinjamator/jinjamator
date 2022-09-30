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
from copy import deepcopy


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
    def __init__(self, name):
        self.__name__ = name

    pass


class ContentPluginLoader(object):
    def __init__(self, parent):
        self._log = logging.getLogger()
        self._filters = {}
        self._functions = {}
        self._parent = parent
        self._base_plugin_imports = []
        if parent:
            self._prepare_import_list()

    def _prepare_import_list(self):
        for content_plugin_dir in self._parent._configuration.get(
            "global_content_plugins_base_dirs", []
        ):
            for tmp in glob.glob(content_plugin_dir + "/*"):
                if tmp.endswith("__init__.py") or tmp.endswith("__pycache__"):
                    continue
                if tmp.endswith(".py"):
                    tmp = tmp[:-3]
                tmp = os.path.basename(tmp)
                self._base_plugin_imports.append(
                    f"import jinjamator.plugins.content.{tmp} as {tmp}"
                )

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
                self._functions[key] = contentPlugin(key)
            cur = self._functions[key]

            for item in tmp:
                if not hasattr(cur, item):
                    setattr(cur, item, contentPlugin(key))
                cur = getattr(cur, item)
            code = "\n".join(self._base_plugin_imports) + "\n"
            with open(file, "r") as fh:
                code += fh.read()
            try:
                module = import_code(code, "jinjamator.plugins.content" + class_path)
            except ImportError as e:
                self._log.error(f"cannot load content plugin {file}. {e}")
                continue

            for func_name in dir(module):
                func = getattr(module, func_name)
                if isinstance(func, types.FunctionType):
                    if sys.modules.get(func.__module__):
                        # self._log.debug(
                        #     f"skipping imported function {class_path}.{func_name}"
                        # )
                        continue
                    # self._log.debug(f"registering {class_path}.{func_name}")

                    setattr(cur, func_name, func)
                    argspec = inspect.getfullargspec(func)
                    if hasattr(self._parent, "parent"):
                        setattr(module, "_jinjamator", self._parent.parent)
                    else:
                        setattr(module, "_jinjamator", self._parent)
                    setattr(module, "__file__", file)
                    # if len(argspec.args) == 1:
                    self._filters[f"{class_path}.{func_name}"] = func

    def get_functions(self):
        return self._functions

    def get_filters(self):
        return self._filters

    def j2_load_plugins(self, env):
        for filter_name, filter in self.get_filters().items():
            if filter_name not in env.filters:
                env.filters[filter_name] = filter
        for function_name, function in self.get_functions().items():
            if function_name not in env.globals:
                env.globals[function_name] = function
        return env

    def py_load_plugins(self, env):
        for function_name, function in self.get_functions().items():
            # global_ldr._log.debug('registred {0}'.format(function_name))
            env[function_name] = function


def task_init_pluginloader(parent, scope):
    ldr = ContentPluginLoader(parent)
    for content_plugin_dir in parent._configuration.get(
        "global_content_plugins_base_dirs", []
    ):
        ldr.load(f"{content_plugin_dir}")
    if os.path.isdir(parent._configuration["taskdir"] + "/plugins/content"):
        ldr._log.debug(
            "found task plugins directory "
            + parent._configuration["taskdir"]
            + "/plugins/content"
        )
        ldr._plugin_ldr.load(parent._configuration["taskdir"] + "/plugins/content")

    ldr.py_load_plugins(scope)
