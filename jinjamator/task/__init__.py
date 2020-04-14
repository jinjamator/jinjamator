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
from .configuration import TaskConfiguration
from jinjamator.plugin_loader.content import (
    j2_load_plugins,
    py_load_plugins,
    init_loader,
    ContentPluginLoader,
)
from natsort import natsorted
import glob
import os
import jinja2
import jinja2.meta as j2_meta
from pyflakes.api import check as pyflakes_check
from pyflakes.reporter import Reporter as pyflakes_reporter
import re
from io import StringIO
from future.utils import iteritems
from getpass import getpass
import importlib
import sys
from collections import defaultdict
import json
from deepmerge.merger import Merger
from jinjamator.external.genson import SchemaBuilder
import dictdiffer
import copy
from distutils.util import strtobool
import traceback
import yaml
from jsonschema import validate as validate_jsonschema
import uuid
from dotty_dict import dotty
from jinjamator.plugin_loader.output import load_output_plugin


def tree():
    return defaultdict(tree)


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


class JinjamatorTask(object):
    def __init__(self, run_mode="background"):

        self._current_tasklet = "jinamator-core"
        self._parent_tasklet = "jinamator-core"
        self._parent_task_id = None
        self._log = logging.getLogger()

        self._tasklets = []
        self.configuration = TaskConfiguration()
        self.configuration["jinjamator_base_directory"] = os.sep.join(
            os.path.dirname(__file__).split(os.sep)[:-2]
        )
        self._supported_file_types = ("*.j2", "*.py")
        self.j2_environment = None
        self._undefined_vars = []
        self._default_values = {}
        self.configuration["task_run_mode"] = run_mode
        if self.configuration["task_run_mode"] == "background":
            sys.stdout = self._stdout = StringIO()
        else:
            self._stdout = sys.stdout

        self._results = tree()
        self._schema_extensions = []

    def load(self, path):
        self.task_base_dir = path

        self._log.debug(f"---------------- load task: {path} ----------------")

        search_paths = self.configuration.get("global_tasks_base_dirs", [])

        self._log.debug(f"task search paths are: {search_paths}")

        if not os.path.isabs(path):
            for global_base_dir in search_paths:
                tried_path = f"{global_base_dir}{os.path.sep}{path}"
                if os.path.exists(tried_path):
                    path = tried_path
                    self._log.debug(f"resolved path to {path}")
                    break

        if os.path.isfile(path):
            self.task_base_dir = os.path.dirname(path)
            self._tasklets = [path]
        elif os.path.isdir(path):
            self.task_base_dir = path
            for file_type in self._supported_file_types:
                self._tasklets.extend(
                    glob.glob("{0}/{1}".format(self.task_base_dir, file_type))
                )
        else:
            raise ValueError(f"cannot load path {path}")

        global_ldr = init_loader(self)
        for content_plugin_dir in self.configuration.get(
            "global_content_plugins_base_dirs", []
        ):
            global_ldr.load(f"{content_plugin_dir}")

        self.setup_jinja2()

        self._tasklets = natsorted(self._tasklets)
        try:
            self._default_values = self.configuration.merge_yaml(
                "{0}/defaults.yaml".format(path)
            )
            self._log.debug("loaded {0}/defaults.yaml".format(path))
            for var in self._undefined_vars:
                if var in self.configuration._data:
                    self._undefined_vars.remove(var)

        except FileNotFoundError:
            pass
        except jinja2.exceptions.TemplateNotFound:
            pass

        if self.configuration["undo"]:
            self.is_undo_run = True
            self._tasklets.reverse()
            self._log.info("undo run detected: reversing task order")
        else:
            self.is_undo_run = False

        if not self._tasklets:
            raise ValueError("no task items found")

        self.analyze_tasklets()

    def setup_jinja2(self):
        j2_loader = jinja2.FileSystemLoader(self.task_base_dir)
        self.j2_environment = jinja2.Environment(
            loader=j2_loader, extensions=["jinja2.ext.do"]
        )
        self.j2_environment.globals["parent"] = self
        self.j2_environment.globals["configuration"] = self.configuration._data
        self.j2_environment.trim_blocks = True
        self.j2_environment.lstrip_blocks = True

        self.j2_environment = j2_load_plugins(self.j2_environment)

    def analyze_j2_tasklet(self, tasklet):
        template_source = self.j2_environment.loader.get_source(
            self.j2_environment, os.path.basename(tasklet)
        )[0]
        parsed_content = self.j2_environment.parse(template_source)
        for undef_var in list(j2_meta.find_undeclared_variables(parsed_content)):
            if (
                undef_var not in self.configuration._data
                and undef_var not in self.j2_environment.globals.keys()
                and undef_var not in self._undefined_vars
            ):
                self._undefined_vars.append(undef_var)

    def get_py_tasklet_code(self, path):
        user_code = ""
        with open(path) as fh:
            user_code = fh.read().split("\n")
            if user_code[0].startswith("#!"):
                del user_code[0]
            task_code = "{0}\n{1}".format(
                'from jinjamator.task.python import PythonTask\n\
import sys,os\n\
from jinjamator.plugin_loader.content import py_load_plugins\n\
py_load_plugins(globals(),"{0}/plugins/content/*.py")\n\
class jinjaTask(PythonTask):\n  def __run__(self):\n'.format(
                    self.task_base_dir
                ),
                "\n".join(["    " + s for s in user_code]),
            )
        return task_code

    def analyze_py_tasklet(self, tasklet):
        tasklet_code = self.get_py_tasklet_code(tasklet)
        errors = StringIO()
        warnings = StringIO()
        reporter = pyflakes_reporter(warnings, errors)
        pyflakes_check(tasklet_code, self.task_base_dir, reporter)
        undefined_vars = re.findall(
            r"(?<=undefined name ')(\S+)(?=')", warnings.getvalue(), re.MULTILINE
        )
        for undef_var in undefined_vars:
            if (
                undef_var not in self.configuration._data
                and undef_var not in self.j2_environment.globals.keys()
                and undef_var not in self._undefined_vars
            ):
                self._undefined_vars.append(undef_var)

    def set_output_plugin(self, output_plugin):
        self._output_plugin = output_plugin

    def load_output_plugin(self, output_plugin_name, search_dirs):
        load_output_plugin(self, output_plugin_name, search_dirs)

    def analyze_tasklets(self):
        for tasklet in self._tasklets:
            self._log.debug("analyzing tasklet {0}".format(tasklet))
            if tasklet.endswith(".j2"):
                self.analyze_j2_tasklet(tasklet)
            elif tasklet.endswith(".py"):
                self.analyze_py_tasklet(tasklet)

    def get_undefined_task_variables(self):
        return self._undefined_vars

    def handle_undefined_var(self, var_name):
        if var_name == "undo":
            self.configuration["undo"] = False
        if var_name == "best_effort":
            self.configuration["best_effort"] = False
        if self.configuration["task_run_mode"] == "background":
            raise KeyError(
                "undefined variable found {0} and running in background -> cannot proceed".format(
                    var_name
                )
            )
        elif self.configuration["task_run_mode"] == "interactive":
            if "pass" in var_name.lower():
                self.configuration[var_name] = getpass("{0}:".format(var_name))
            else:
                inp = input("{0}:".format(var_name))
                self.configuration[var_name] = inp
                try:
                    self.configuration[var_name] = json.loads(inp)
                except:
                    pass
                try:
                    self.configuration[var_name] = int(inp)
                except:
                    pass
                if inp in ["None", None, "none"]:
                    self.configuration[var_name] = None
                if inp in ["True", True, "true", "yes", "Yes", "y", "Y"]:
                    self.configuration[var_name] = True
                if inp in ["False", False, "false", "no", "No", "n", "N"]:
                    self.configuration[var_name] = False

        else:
            raise Exception(
                "run mode {0} not implemented".format(
                    self.configuration["task_run_mode"]
                )
            )

        return self.configuration[var_name]

    def enhance_schema(self, obj, name="root"):
        title = ""
        for word in name.split("_"):
            title = title + word.capitalize() + " "
        title = title.strip()
        if isinstance(obj, str):
            retval = {"title": title}
            return retval

        elif isinstance(obj, float):
            retval = {"title": title}
            return retval

        elif isinstance(obj, int):
            retval = {"title": title}
            return retval
        elif obj is None:
            retval = {"title": title}
            return retval
        elif isinstance(obj, list):
            retval = {"title": title, "items": {}}

            m = Merger(
                [(list, ["append"]), (dict, ["merge"])], ["override"], ["override"]
            )

            for value in obj:
                if name.endswith("es"):
                    name = name[:-2]
                elif name.endswith("s"):
                    name = name[:-1]
                for k, v in self.enhance_schema(value, name).items():
                    m.merge(retval["items"], {k: v})

            return retval
        elif isinstance(obj, dict):
            retval = {"title": title, "properties": {}}

            for k, v in obj.items():
                retval["properties"][k] = self.enhance_schema(v, k)
            return retval

        return obj

    def load_schema_yaml(self, path):
        from pprint import pformat

        try:
            with open(path, "r") as stream:
                try:
                    raw_data = stream.read()

                    environment = jinja2.Environment(extensions=["jinja2.ext.do"])
                    environment = j2_load_plugins(environment)
                    parsed_data = environment.from_string(raw_data).render(
                        self.configuration._data
                    )
                    final_data = dotty(yaml.safe_load(parsed_data))

                    for schema_extension in self._schema_extensions:

                        for key, value in schema_extension["data"].items():
                            if schema_extension["path"] != ".":
                                # self._log.error(pformat(final_data))
                                final_data[schema_extension["path"]][key] = value[
                                    "schema"
                                ]
                                if value.get("options"):
                                    options_path = (
                                        schema_extension["path"]
                                        .replace("schema", "options")
                                        .replace("properties", "items")
                                    )
                                    final_data[options_path][key] = value["options"]
                            else:

                                final_data.update({key: value})

                    final_data = final_data.to_dict()
                    # self._log.error(pformat(final_data))

                    if not final_data:
                        final_data = {}
                    return final_data
                except yaml.YAMLError as e:
                    self._log.error(e)
        except IOError:
            self._log.debug("{0} not found".format(path))
            pass
        return {}

    def get_jsonform_schema(self):

        try:
            with open(self.task_base_dir + "/form.json") as fh:
                return json.loads(fh.read())
        except IOError:
            self._log.debug(
                "no form schema definition found for task {0} -> auto generating".format(
                    self.task_base_dir
                )
            )
            pass

        # schema_settings = TaskConfiguration()
        # schema_settings.merge_dict(self.configuration._data)
        # schema_settings.merge_yaml(self.task_base_dir + '/schema.yaml','merge','exclusive','override','override')
        schema_settings = self.load_schema_yaml(self.task_base_dir + "/schema.yaml")

        schema = tree()
        schema["schema"]["title"] = (
            "Create Job for: <strong>" + self.task_base_dir + "</strong>"
        )
        schema["schema"]["type"] = "object"
        schema["view"]["wizard"] = {
            "title": "Welcome to the Wizard",
            "description": "Please fill things in as you wish",
            "bindings": tree(),
            "steps": [
                {
                    "title": "Task Configuration (1/2)",
                    "description": "Required Information",
                },
                {
                    "title": "Task Configuration (2/2)",
                    "description": "Optional Information",
                },
                {"title": "Job Configuration", "description": "Required Information"},
            ],
        }

        # schema['view']['templates']['container-array-actionbar']='#ationbar'
        schema["options"]["hideInitValidationError"] = True

        undefined_vars = self.get_undefined_task_variables()

        tmp = copy.deepcopy(self.configuration._data)
        del tmp["task_run_mode"]
        del tmp["jinjamator_base_directory"]

        diff = dictdiffer.diff(self._default_values, tmp)

        external_vars = dictdiffer.patch(diff, tree())

        diff = dictdiffer.diff(external_vars, tmp)
        self._default_values = dictdiffer.patch(diff, tmp)

        for var in undefined_vars:
            if var not in ["undo"]:
                title = ""
                for word in var.split("_"):
                    title = title + word.capitalize() + " "

                schema["schema"]["properties"][var]["title"] = title.strip()
                schema["schema"]["properties"][var]["type"] = "string"
                # schema['schema']['properties'][var]['description']=''
                schema["schema"]["properties"][var]["required"] = True
                if "pass" in var:
                    schema["schema"]["properties"][var]["format"] = "password"
                schema["view"]["wizard"]["bindings"][var] = 1

        for var, value in external_vars.items():
            if var not in ["undo"]:
                title = ""
                for word in var.split("_"):
                    title = title + word.capitalize() + " "

                schema["schema"]["properties"][var]["title"] = title.strip()
                schema["schema"]["properties"][var]["type"] = "string"
                schema["schema"]["properties"][var]["description"] = ""
                schema["schema"]["properties"][var]["required"] = True
                schema["schema"]["properties"][var]["default"] = value
                if "pass" in var:
                    schema["schema"]["properties"][var]["format"] = "password"
                schema["view"]["wizard"]["bindings"][var] = 1

        if not undefined_vars and not external_vars.keys():
            schema["schema"]["properties"]["no_required_vars"][
                "title"
            ] = "Task has no undefined variables"
            schema["schema"]["properties"]["no_required_vars"]["type"] = "string"
            schema["schema"]["properties"]["no_required_vars"]["description"] = ""
            schema["schema"]["properties"]["no_required_vars"]["required"] = False
            schema["schema"]["properties"]["no_required_vars"]["default"] = ""
            schema["options"]["fields"]["no_required_vars"]["readonly"] = True
            schema["view"]["wizard"]["bindings"]["no_required_vars"] = 1

        if self._default_values:
            builder = SchemaBuilder()
            builder.add_object(self._default_values)
            m = Merger(
                [(list, ["append"]), (dict, ["merge"])], ["override"], ["override"]
            )

            for k, v in builder.to_schema()["properties"].items():
                schema["schema"]["properties"][k] = v
                schema["view"]["wizard"]["bindings"][k] = 2
                schema["data"][k] = self._default_values[k]
                enhanced = self.enhance_schema(self._default_values[k], k)
                m.merge(schema["schema"]["properties"][k], enhanced)

        else:
            schema["schema"]["properties"]["no_default_vars"][
                "title"
            ] = "Task has no default variables"
            schema["schema"]["properties"]["no_default_vars"]["type"] = "string"
            schema["schema"]["properties"]["no_default_vars"]["description"] = ""
            schema["schema"]["properties"]["no_default_vars"]["required"] = False
            schema["schema"]["properties"]["no_default_vars"]["default"] = ""
            schema["options"]["fields"]["no_default_vars"]["readonly"] = True
            schema["view"]["wizard"]["bindings"]["no_default_vars"] = 2

        schema["view"]["parent"] = "bootstrap-edit-horizontal"

        schema["schema"]["properties"]["task"]["type"] = "string"
        schema["schema"]["properties"]["task"]["default"] = self.task_base_dir
        schema["schema"]["properties"]["task"]["required"] = True
        schema["options"]["fields"]["task"]["type"] = "hidden"

        schema["schema"]["properties"]["jinjamator_job_id"]["type"] = "string"
        schema["schema"]["properties"]["jinjamator_job_id"]["default"] = uuid.uuid4()
        schema["schema"]["properties"]["jinjamator_job_id"]["required"] = True
        schema["options"]["fields"]["jinjamator_job_id"]["type"] = "hidden"

        schema["schema"]["properties"]["output_plugin"]["title"] = "Output Plugin"
        schema["schema"]["properties"]["output_plugin"]["type"] = "string"
        schema["schema"]["properties"]["output_plugin"]["enum"] = [
            "apic",
            "console",
            "ssh",
            "textfile",
            "xlsxfile",
            "csvfile",
            "rabbitmq",
        ]
        schema["schema"]["properties"]["output_plugin"]["default"] = "console"
        schema["schema"]["properties"]["output_plugin"]["required"] = True
        schema["options"]["fields"]["output_plugin"][
            "helper"
        ] = "Select the output plugin which jinjamator uses to process the tasklet return values"
        schema["options"]["fields"]["output_plugin"]["onFieldChange"] = ""

        schema["view"]["wizard"]["bindings"]["output_plugin"] = 3
        schema["view"]["wizard"]["bindings"]["undo"] = 3
        schema["view"]["wizard"]["bindings"]["best_effort"] = 3

        schema["schema"]["properties"]["custom_parameters"][
            "title"
        ] = "Custom Variables"
        schema["schema"]["properties"]["custom_parameters"]["type"] = "array"
        schema["schema"]["properties"]["custom_parameters"][
            "description"
        ] = "add custom variable definitions for this run"
        schema["schema"]["properties"]["custom_parameters"]["items"]["type"] = "object"
        schema["schema"]["properties"]["custom_parameters"]["items"]["properties"][
            "key"
        ]["title"] = "Variable Name"
        schema["schema"]["properties"]["custom_parameters"]["items"]["properties"][
            "key"
        ]["type"] = "string"
        schema["schema"]["properties"]["custom_parameters"]["items"]["properties"][
            "key"
        ]["required"] = True

        schema["schema"]["properties"]["custom_parameters"]["items"]["properties"][
            "value"
        ]["title"] = "Value"
        schema["schema"]["properties"]["custom_parameters"]["items"]["properties"][
            "value"
        ]["type"] = "string"

        schema["schema"]["properties"]["output_plugin_parameters"][
            "title"
        ] = "Output Plugin Parameters"
        schema["schema"]["properties"]["output_plugin_parameters"]["type"] = "array"

        schema["schema"]["properties"]["custom_parameters"]["required"] = False
        schema["view"]["wizard"]["bindings"]["custom_parameters"] = 3
        schema["view"]["wizard"]["bindings"]["output_plugin_parameters"] = 3

        schema["schema"]["properties"]["undo"]["title"] = "Undo"
        schema["schema"]["properties"]["undo"]["type"] = "boolean"

        schema["schema"]["properties"]["best_effort"]["title"] = "Best Effort"
        schema["schema"]["properties"]["best_effort"]["type"] = "boolean"
        # schema['options']['fields']['best_effort']['order']=''

        try:
            schema["schema"]["properties"]["undo"]["default"] = bool(
                strtobool(self.configuration._data["undo"])
            )
        except:
            schema["schema"]["properties"]["undo"]["default"] = False
        schema["options"]["fields"]["undo"][
            "helper"
        ] = "Run Task in undo mode if supported"

        m = Merger(
            [(list, ["override"]), (dict, ["merge"])], ["override"], ["override"]
        )

        for key, value in schema["schema"]["properties"].items():
            try:
                m.merge(
                    schema["schema"]["properties"][key], schema_settings[key]["schema"]
                )
            except:
                pass
            try:
                m.merge(
                    schema["options"]["fields"][key], schema_settings[key]["options"]
                )
            except:
                pass
            try:
                schema["view"]["wizard"]["bindings"][key] = schema_settings[key][
                    "form_step"
                ]
            except:
                pass
            try:
                schema["data"][key] = schema_settings[key]["data"]
            except:
                pass
            try:
                schema["schema"]["dependencies"][key] = schema_settings[key][
                    "dependencies"
                ]
            except:
                pass
        return schema

    def run(self):
        if len(self._undefined_vars) > 0:
            if self.configuration["task_run_mode"] == "background":
                raise Exception(
                    "cannot run task because of undefined variables: {0}".format(
                        self._undefined_vars
                    )
                )
            else:
                for var in self._undefined_vars:
                    self.handle_undefined_var(var)

        schema = self.get_jsonform_schema()["schema"]
        del schema["properties"]["custom_parameters"]
        del schema["properties"]["output_plugin"]
        del schema["properties"]["task"]

        # validate_jsonschema(instance=self.configuration._data, schema=schema)
        # validate_jsonschema(instance=self.configuration._data, schema=self._output_plugin.get_json_schema(self.configuration._data)['schema'])
        results = {}
        for tasklet in self._tasklets:
            self._current_tasklet = tasklet
            retval = ""
            self._log.debug(
                "running with dataset: {0}".format(self.configuration._data)
            )
            if tasklet.endswith("j2"):
                try:
                    t = self.j2_environment.get_template(os.path.basename(tasklet))
                    retval = t.render(self.configuration)
                except jinja2.exceptions.UndefinedError as e:
                    self._log.error(
                        "{0}\n{1} -> skipping tasklet {2}".format(
                            traceback.format_exc(), e.message, tasklet
                        )
                    )
                except IndexError as e:
                    self._log.error(
                        "{0}\n{1} -> skipping tasklet {2}".format(
                            traceback.format_exc(), e.message, tasklet
                        )
                    )
                pass
            elif tasklet.endswith("py"):
                task_code = self.get_py_tasklet_code(tasklet)
                self._log.debug(task_code)
                module = import_code(task_code, tasklet[:-3].replace("/", "."))
                for k, v in iteritems(self.configuration._data):
                    setattr(module, k, v)

                setattr(module, "__file__", tasklet)
                setattr(module.jinjaTask, "parent", self)
                setattr(module.jinjaTask, "configuration", self.configuration._data)
                module._log = self._log
                try:
                    retval = module.jinjaTask().__run__()
                except Exception as e:
                    _, _, tb = sys.exc_info()
                    filename, lineno, funname, line = traceback.extract_tb(tb)[-1]
                    if filename == "<string>":
                        filename = tasklet
                        code_to_show = task_code.split("\n")[lineno - 1]
                    else:
                        code_to_show = ""

                    self._log.error(
                        "{}\n{}:{}, in {}\n    {}\n{}".format(
                            e, tasklet, lineno, funname, line, code_to_show
                        )
                    )
                    if self.configuration._data["best_effort"]:
                        continue
                    else:
                        self._log.error(
                            "tasklet {0} has failed and best_effort is not defined -> exiting".format(
                                tasklet
                            )
                        )
                        return False

            else:
                raise ValueError(
                    "tasklet {0} has file extension which is not supported".format(
                        tasklet
                    )
                )

            self._output_plugin.init_plugin_params()
            self._output_plugin.connect()
            self._output_plugin.process(
                retval, template_path=tasklet, current_data=self.configuration
            )

            results[tasklet] = retval
            if self.configuration["task_run_mode"] == "background":
                self._log.tasklet_result(
                    "{0}".format(retval)
                )  # this submits the result via celery
        return results
