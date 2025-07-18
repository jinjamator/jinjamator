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
from deepmerge.merger import Merger
from deepmerge.strategy.core import STRATEGY_END
import yaml
import jinja2
from jinjamator.plugin_loader.content import ContentPluginLoader
import json
from jinja2 import Undefined, meta 
from copy import deepcopy
from jinjamator.tools.password import redact
import types
from str2bool3.str_utils import str2bool_exc

class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
    def ignore_unknown(self, node):
        return None


SafeLoaderIgnoreUnknown.add_constructor(None, SafeLoaderIgnoreUnknown.ignore_unknown)


class SilentUndefined(Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        class EmptyString(str):
            def __call__(self, *args, **kwargs):
                return ""

        return EmptyString()

    __add__ = (
        __radd__
    ) = (
        __mul__
    ) = (
        __rmul__
    ) = (
        __div__
    ) = (
        __rdiv__
    ) = (
        __truediv__
    ) = (
        __rtruediv__
    ) = (
        __floordiv__
    ) = (
        __rfloordiv__
    ) = (
        __mod__
    ) = (
        __rmod__
    ) = (
        __pos__
    ) = (
        __neg__
    ) = (
        __call__
    ) = (
        __getitem__
    ) = (
        __lt__
    ) = (
        __le__
    ) = (
        __gt__
    ) = (
        __ge__
    ) = (
        __int__
    ) = __float__ = __complex__ = __pow__ = __rpow__ = _fail_with_undefined_error


class TaskConfiguration(object):
    def __init__(self):
        self._log = logging.getLogger()
        self._data = {}
        self._plugin_loader = None
        

    def __getitem__(self, item):
        try:
            return self._data[item]
        except KeyError:
            return None

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        try:
            self._data.__delitem__(key)
        except:
            pass

    def __str__(self):
        tmp = redact(deepcopy(self._data))[1]
        return str(tmp)

    def __str__(self):
        tmp = redact(deepcopy(self._data))[1]
        return str(tmp)

    def get(self, item_name, default=False):
        return self._data.get(item_name, default)

    def keys(self):
        return self._data.keys()

    def exclusive_merge_list(self, config, path, base, nxt):
        """a list strategy to append elements if not already in list."""
        return base + [i for i in nxt if i not in base]

    def use_existing_list(self, config, path, base, nxt):
        print(base,nxt)
        if not base:
            return nxt
        return base

    def use_existing_dict(self, config, path, base, nxt):
        for k,v in nxt.items():
            if k in base:
                continue
            base[k]=v
        return base

    def merge_dict(
        self,
        dict_data,
        dict_strategy="merge",
        list_strategy="exclusive",
        other_types_strategy="use_existing",
        type_conflict_strategy="use_existing",
    ):
        if list_strategy == "exclusive":
            list_strategy = self.exclusive_merge_list
        elif list_strategy == "use_existing":
            list_strategy = self.use_existing_list
        if dict_strategy == "use_existing":
            dict_strategy=self.use_existing_dict
        # else:
        #    list_strategy = [list_strategy]
        m = Merger(
            [(list, list_strategy), (dict, [dict_strategy])],
            [other_types_strategy],
            [type_conflict_strategy],
        )

        m.merge(self._data, dict_data)
        if "mapping" in dict_data.keys():
            self.extract_vars_from_mapping()

    def merge_list(self, list1, list2):
        return list1 + [i for i in list2 if i not in list1]

    def run_j2(self, template, undef_ok=False):
        if undef_ok:
            environment = jinja2.Environment(
                extensions=["jinja2.ext.do"], undefined=SilentUndefined
            )
        else:
            environment = jinja2.Environment(extensions=["jinja2.ext.do"])
            environment = self._plugin_loader.j2_load_plugins(environment)
        return environment.from_string(template).render(self._data)

    def merge_yaml(
        self,
        path,
        dict_strategy="merge",
        list_strategy="exclusive",
        other_types_strategy="use_existing",
        type_conflict_strategy="use_existing",
        private_data=None,
    ):
        try:
            with open(path, "r") as stream:
                try:
                    raw_data = stream.read()
                    tmp = []
                    for l in raw_data.split("\n"):
                        if (
                            "{{" not in l
                            and "}}" not in l
                            and "{%" not in l
                            and "%}" not in l
                        ):
                            tmp.append(l)
                    parsed_raw_data = yaml.safe_load("\n".join(tmp))
                    if not parsed_raw_data:
                        parsed_raw_data = {}
                    for k, v in self._data.items():
                        if k not in list(parsed_raw_data.keys()):
                            parsed_raw_data[k] = v
                    backup_data={}
                    if self._plugin_loader._parent:
                        try:
                            data_backup = deepcopy(
                                self._plugin_loader._parent.configuration._data
                            )
                            self._plugin_loader._parent.configuration._data = {
                                **self._plugin_loader._parent.configuration._data,
                                **parsed_raw_data,
                            }
                        except AttributeError:
                            data_backup = deepcopy(
                                self._plugin_loader._parent.configuration
                            )
                            self._plugin_loader._parent.configuration = {
                                **self._plugin_loader._parent.configuration,
                                **parsed_raw_data,
                            }

                    environment = jinja2.Environment(extensions=["jinja2.ext.do"])

                    ast = environment.parse(raw_data)
                    _jinjamator=self._plugin_loader._parent
                    for var in meta.find_undeclared_variables(ast):
                        for command in self._plugin_loader.get_functions():
                            if command.startswith(var):
                                if command in raw_data:
                                    try:
                                        var_dependencies=self._plugin_loader.get_functions()[command].__kwdefaults__.get('_requires',print)
                                        if isinstance(var_dependencies, types.FunctionType):
                                            for dep_var in var_dependencies():
                                                if dep_var not in _jinjamator._undefined_vars:
                                                    _jinjamator._undefined_vars.append(dep_var)
                                        if isinstance(var_dependencies, types.list):
                                            for dep_var in var_dependencies:
                                                if dep_var not in _jinjamator._undefined_vars:
                                                    _jinjamator._undefined_vars.append(dep_var)
                                    except AttributeError:
                                        pass
                                    
                    environment = self._plugin_loader.j2_load_plugins(environment)

                    parsed_raw_data["configuration"] = self._data
                    if private_data:
                        parsed_raw_data["_configuration"] = deepcopy(private_data)
                    try:
                        parsed_data = environment.from_string(raw_data).render(
                            parsed_raw_data
                        )
                    except jinja2.exceptions.UndefinedError as e:

                        self._log.error(e)
                        self._log.error(raw_data)
                        self._log.error(parsed_raw_data)
                        self._log.error(environment.globals)
                        self._log.error(environment.filters)
                        self._log.error("retry 1")
                        breakpoint()

                        environment = self._plugin_loader.j2_load_plugins(environment)
                        parsed_data = environment.from_string(raw_data).render(
                            parsed_raw_data
                        )

                    final_data = yaml.safe_load(parsed_data)
                    if self._plugin_loader._parent:
                        self._plugin_loader._parent.configuration._data = data_backup
                    if not final_data:
                        final_data = {}
                    
                    self.merge_dict(
                        final_data,
                        dict_strategy,
                        list_strategy,
                        other_types_strategy,
                        type_conflict_strategy,
                    )

                    return final_data
                except yaml.YAMLError as e:
                    self._log.error(e)
        except IOError:
            self._log.debug("{0} not found".format(path))
            pass
        return {}

    def extract_vars_from_mapping(self):
        if "mapping" in self._data.keys():
            if self._data["mapping"]:
                for mapping in self._data["mapping"]:
                    _map = mapping.split(":")
                    try:
                        val = ":".join(_map[1:])
                        try:
                            self._data[_map[0]] = int(val)
                            continue
                        except ValueError:
                            pass
                        try:
                            self._data[_map[0]] = bool(str2bool_exc(val))
                            continue
                        except ValueError:
                            pass
                        try:
                            self._data[_map[0]] = json.loads(val)
                            continue
                        except ValueError:
                            pass
                        self._data[_map[0]] = val

                    except IndexError:
                        self._log.error(
                            "Invalid mapping detected: {0} -> skipping".format(mapping)
                        )
                del self._data["mapping"]
