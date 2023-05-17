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
from typing import Any
from deepmerge.merger import Merger
from deepmerge.strategy.core import STRATEGY_END
import yaml
import jinja2
from jinjamator.plugin_loader.content import j2_load_plugins

# import distutils.util
import json
from jinja2 import Undefined, meta
from copy import deepcopy
from jinjamator.tools.password import redact
import types
import traceback
import sys

log = logging.getLogger()


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
        # self._plugin_loader = None

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
            environment = j2_load_plugins(environment)
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
                    if '_jinjamator' in __builtins__:
                        backup_data=_jinjamator.configuration._data
                        _jinjamator.configuration._data ={
                            **_jinjamator.configuration._data,
                            **parsed_raw_data
                        }

                    environment = jinja2.Environment(extensions=["jinja2.ext.do"])
                    if '_jinjamator' in __builtins__:
                        ast = environment.parse(raw_data)
                        for var in meta.find_undeclared_variables(ast):
                            for command in __builtins__['all_registered_j2_functions']:
                                if command.startswith(var):
                                    if command in raw_data:
                                        try:
                                            var_dependencies=__builtins__['all_registered_j2_functions'][command].__kwdefaults__.get('_requires',print)
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

                        for var in deepcopy(_jinjamator._undefined_vars):
                            self._data[var]=_jinjamator.handle_undefined_var(var)


                    environment = j2_load_plugins(environment)

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

                        environment = j2_load_plugins(environment)
                        parsed_data = environment.from_string(raw_data).render(
                            parsed_raw_data
                        )


                    final_data = yaml.safe_load(parsed_data)

                    if not final_data:
                        final_data = {}

                    if backup_data:
                        _jinjamator.configuration._data=backup_data

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
                            self._data[_map[0]] = bool(distutils.util.strtobool(val))
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



def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))


class JinjamatorConfigurationLoader(object):
    pass


class JinjamatorConfigurationMappingLoader(JinjamatorConfigurationLoader):
    def load(self, mapping_data: list) -> dict:
        retval = {}
        for mapping in mapping_data:
            try:
                if ":" not in mapping:
                    raise ValueError(f"Mapping contains no semicolon")
                _map = mapping.split(":")
                val = ":".join(_map[1:])
            except (IndexError, ValueError) as e:
                logging.error(f"Invalid mapping detected. {e}: {mapping} -> skipping")
                traceback.print_stack(f=sys._getframe(-1).f_back)
                continue
            try:
                retval[_map[0]] = int(val)
                continue
            except ValueError:
                pass
            try:
                retval[_map[0]] = bool(strtobool(val))
                continue
            except ValueError:
                pass
            try:
                retval[_map[0]] = json.loads(val)
                continue
            except ValueError:
                pass
            retval[_map[0]] = val
        return retval


class JinjamatorConfigurationYAMLLoader(JinjamatorConfigurationLoader):
    pass


class TaskConfigurationSource(object):
    def __init__(self, name: str, priority: int):
        self._name = name
        self._priority = priority
        self._data = {}

    @property
    def name(self) -> str:
        return str(self._name)

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value: dict) -> None:
        if self._data:
            raise ValueError(f"Cannot set data of {self.name} as data already set.")
        if isinstance(value, dict):
            self._data = value
        else:
            raise TypeError(
                f"Invalid type {value.__class__.__name__ }. Allowed types are: dict"
            )

    def __repr__(self) -> str:
        tmp = redact(deepcopy(self._data))[1]
        try:
            from prettytable import PrettyTable

            table = PrettyTable(["parameter name", "value"])
            table.align = "l"
            for k, v in tmp.items():
                table.add_row(
                    [
                        k,
                        json.dumps(
                            v,
                            indent=2,
                            sort_keys=True,
                        ),
                    ]
                )
            return f"{self.name}, priority {self.priority}:\n" + str(table)
        except ImportError:
            return "\n".join(json.dumps(tmp, indent=2, sort_keys=True))


class ConfigurationSources(object):
    def __init__(self, __parent):
        self.__sources_by_priority = {}
        self.__sources_by_name = {}
        self.__parent = __parent

    def __repr__(self) -> str:
        try:
            from prettytable import PrettyTable

            table = PrettyTable(["priority", "name"])
            table.align = "l"
            for k, v in self.__sources_by_priority.items():
                table.add_row([k, v.name])
            return "ConfigurationSources:\n" + str(table)
        except ImportError:
            return "\n".join(
                [f"{v.priority}:{v.name}" for v in self.__sources_by_priority.values()]
            )

    @property
    def by_priority(self) -> dict:
        return self.__sources_by_priority

    @property
    def by_name(self) -> dict:
        return self.__sources_by_name

    def add(self, name: str, priority: int):
        if priority in self.__sources_by_priority:
            raise ValueError(
                f"Priority {priority} with already defined by {self.__sources[priority].name}"
            )
        if name in self.__sources_by_name:
            raise ValueError(
                f"Priority {priority} with already defined by {self.__sources[priority].name}"
            )
        new_source = TaskConfigurationSource(name, priority)
        self.__sources_by_priority[priority] = new_source

        self.__sources_by_name[name] = new_source


class AccessViolation(Exception):
    pass


class Configuration(object):
    def __init__(self):
        self._sources = ConfigurationSources(self)
        self._sources.add("runtime", 1)  # eg. -o -l etc.
        self._sources.add("cli_explicit_parameter", 10)  # eg. -o -l etc.
        self._sources.add("cli_mapping_parameter", 20)  # -m asdf:qwer
        self._sources.add("cli_global_environment", 30)  # -m asdf:qwer
        self._sources.add("environment_site", 40)  # -m asdf:qwer
        self._sources.add("task_defaults_defaults_yaml", 50)  # -m asdf:qwer
        self._sources.add("task_defaults_schema_yaml", 60)  # -m asdf:qwer
        self._sources.add(
            "cli_parameter_default", 1000
        )  # added by plugins and core but filled with default. Just vars not stating with _.
        self.__current_configuration = {}
        self.dirty = True

    def update(self):
        for prio in sorted(self._sources.by_priority, reverse=True):
            logging.debug(
                f"merging in {self._sources.by_priority[prio].name} with priority {prio}"
            )
            self.__current_configuration.update(self._sources.by_priority[prio].data)
        self.dirty = False

        return True

    @property
    def dirty(self):
        return self._is_dirty

    @dirty.setter
    def dirty(self, value: bool):
        if value.__class__.__name__ != "bool":
            raise TypeError("Value must be bool")
        logging.debug(f"Setting configuration at {hex(id(self))} dirty to {value}")
        self._is_dirty = value

    def __getattr__(self, name_or_id: str | int) -> TaskConfigurationSource | None:
        if name_or_id in self._sources.by_name:
            return self._sources.by_name[name_or_id]
        if name_or_id in self._sources.by_priority:
            return self._sources.by_priority[name_or_id]
        return None

    def __getattribute__(self, __name: str) -> Any:
        if __name.startswith("__"):
            raise AccessViolation(
                f"Tried to directly access protected variable {__name}"
            )
        if __name == "_data":
            log.warning(f"usage of deprecated access to configuration._data")
            traceback.print_stack(f=sys._getframe(-1).f_back)
            return self.__current_configuration

        return super(Configuration, self).__getattribute__(__name)

    def __getitem__(self, key: Any) -> Any:
        if self._is_dirty:
            self.update()
        return self.__current_configuration.get(key)

    def get(self, key):
        return self.__getitem__(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        self._sources.runtime.data[key] = value
        self.__current_configuration[key] = value

    def __delitem__(self, key: Any) -> None:
        del self.__current_configuration[key]

    def __iter__(self):
        return iter(self.__current_configuration)

    def __len__(self) -> int:
        return len(self.__current_configuration)

    def __repr__(self):
        tmp = redact(deepcopy(self.__current_configuration))[1]
        return repr(tmp)


if __name__ == "__main__":
    # this should be converted to proper testcases
    logging.basicConfig(
        format="[%(levelname)s] %(asctime)s %(message)s", level=logging.DEBUG
    )
    test_config = Configuration()
    mapping_loader = JinjamatorConfigurationMappingLoader()
    test_config.cli_mapping_parameter.data = mapping_loader.load(
        [
            "string1:mapping",
            "mapping_string:qwer",
            "mapping_invalid_1",
            "mapping_boolean:True",
            'j1:{"mapping_json_list_key1":["val1","val2"]}',
        ]
    )

    assert (
        test_config.cli_explicit_parameter.data == {}
    ), "Empty TaskConfigurationSource.data should be {}"

    assert (
        test_config.cli_explicit_parameter_non_exising == None
    ), "Non existiing TaskConfigurationSource should be None"

    try:
        test_config.cli_explicit_parameter.data = ("invalid_datatype", "qwer")
        print("test to set wrong datatype: ", "not ok")
    except TypeError:
        print("test to set wrong datatype: ", "ok")
    test_config.cli_explicit_parameter.data = {
        "string1":"explicit",
        "explicit_string1": "value1",
        "explicit_dict1": {"dict1_key1": "dict1_value1", "pass": "##secret@@"},
    }

    try:
        test_config.cli_explicit_parameter.data = {"string1": "value1"}
        print("test to set data twice: ", "not ok")
    except ValueError:
        print("test to set data twice: ", "ok")

    assert "##secret@@" not in str(
        test_config.cli_explicit_parameter
    ), "Password redaction is broken"

    assert "##secret@@" not in str(test_config), "Password redaction is broken"

    print(test_config.cli_explicit_parameter)
    print(test_config["string1"])
    print(json.dumps(test_config._data,indent=2))
