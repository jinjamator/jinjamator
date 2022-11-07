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

from distutils.command.upload import upload
import logging
from .configuration import TaskConfiguration
from jinjamator.plugin_loader.content import (
    ContentPluginLoader,
)
from natsort import natsorted
import glob
import os
import jinja2
import jinja2.meta as j2_meta
from pyflakes.api import check as pyflakes_check
from pyflakes.reporter import Reporter as pyflakes_reporter
import pyflakes.messages
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
from pprint import pformat
import types
from jinja2 import nodes
import tempfile
from jinjamator.tools.password import redact
from copy import deepcopy


class CustomUndefinedName(pyflakes.messages.Message):
    message = "undefined name %r %r %r %r %r"

    def __init__(self, filename, loc, name):
        pyflakes.messages.Message.__init__(self, filename, loc)
        self.message_args = (
            name,
            loc.lineno,
            loc.col_offset,
            loc.end_lineno,
            loc.end_col_offset,
        )


pyflakes.messages.UndefinedName = CustomUndefinedName


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


class JinjamatorTaskRunException(BaseException):
    pass


class TaskletFailed(ValueError):
    def __init__(self, results, message):
        self.results = results
        self.message = message
        super().__init__(self.message)


class JinjamatorTask(object):
    def __init__(self, run_mode="background"):
        self._plugin_ldr = None
        self._current_tasklet = "jinamator-core"
        self._parent_tasklet = "jinamator-core"
        self._parent_task_id = None
        self._log = logging.getLogger()
        self._id = id(self)
        self._current_global_base_dir = None
        self._unresolved_task_base_dir = None
        self._tasklets = []
        self.configuration = TaskConfiguration()
        self._configuration = TaskConfiguration()
        self._configuration["jinjamator_base_directory"] = os.sep.join(
            os.path.dirname(__file__).split(os.sep)[:-2]
        )
        self._supported_file_types = ("*.j2", "*.py")
        self.j2_environment = None
        self._undefined_vars = []
        self._default_values = {}
        self._configuration["task_run_mode"] = run_mode
        if self._configuration["task_run_mode"] == "background":
            sys.stdout = self._stdout = StringIO()
        else:
            self._stdout = sys.stdout

        self._results = tree()
        self._schema_extensions = []
        self._celery = None

    def load(self, path):
        self.task_base_dir = path
        self._unresolved_task_base_dir = path
        self._log.debug(f"---------------- load task: {path} ----------------")

        search_paths = self._configuration.get("global_tasks_base_dirs", [])

        self._log.debug(f"task search paths are: {search_paths}")

        if not os.path.isabs(path):
            for global_base_dir in search_paths:
                tried_path = os.path.join(global_base_dir, path)
                if os.path.exists(tried_path):
                    self._log.debug(f"resolved path to {tried_path}")
                    self._current_global_base_dir = global_base_dir
                    path = tried_path
                    break

        if os.path.isfile(path):
            self.task_base_dir = os.path.dirname(path)
            self._tasklets = [path]
            path = self.task_base_dir
            self._configuration["taskdir"] = self.task_base_dir

        elif os.path.isdir(path):
            self.task_base_dir = path
            self._configuration["taskdir"] = path
            for file_type in self._supported_file_types:
                self._tasklets.extend(
                    glob.glob("{0}/{1}".format(self.task_base_dir, file_type))
                )
        else:
            raise ValueError(f"cannot load path {path}")

        self._plugin_ldr = ContentPluginLoader(self)
        if os.path.isdir(self._configuration["taskdir"] + "/plugins/content"):
            self._log.debug(
                "found task plugins directory "
                + self._configuration["taskdir"]
                + "/plugins/content"
            )
            self._plugin_ldr.load(self._configuration["taskdir"] + "/plugins/content")

        for content_plugin_dir in self._configuration.get(
            "global_content_plugins_base_dirs", []
        ):
            self._plugin_ldr.load(f"{content_plugin_dir}")

        self.configuration._plugin_loader = self._plugin_ldr
        self._configuration._plugin_loader = self._plugin_ldr
        self.setup_jinja2()

        self._tasklets = natsorted(self._tasklets)
        try:
            self._default_values = self.configuration.merge_yaml(
                "{0}/defaults.yaml".format(path), private_data=self._configuration._data
            )
            self._log.debug("loaded {0}/defaults.yaml".format(path))
            for var in self._undefined_vars:
                if var in self.configuration._data:
                    self._undefined_vars.remove(var)
                if var in self._configuration._data:
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
        self.j2_environment.globals["_configuration"] = self._configuration._data
        self.j2_environment.trim_blocks = True
        self.j2_environment.lstrip_blocks = True

        self.j2_environment = self._plugin_ldr.j2_load_plugins(self.j2_environment)

    def find_calls(self, ast):
        """Find all the nodes of a given type.  If the type is a tuple,
        the check is performed for any of the tuple items.
        """
        for child in ast.iter_child_nodes():
            if isinstance(child, nodes.Call):
                yield child
            else:
                for result in self.find_calls(child):
                    yield result

    def resolve_function_name(self, node):
        try:
            retval = node.attr
        except:
            retval = node.name

        try:
            retval = self.resolve_function_name(node.node) + "." + retval
        except AttributeError:
            pass
        return retval

    def function_calls(self, ast):
        """Return function calls"""

        results = []
        for i, node in enumerate(self.find_calls(ast)):
            results.append(self.resolve_function_name(node.node))
        return results

    def analyze_j2_tasklet(self, tasklet):
        template_source = self.j2_environment.loader.get_source(
            self.j2_environment, os.path.basename(tasklet)
        )[0]
        parsed_content = self.j2_environment.parse(template_source)

        for undef_var in list(j2_meta.find_undeclared_variables(parsed_content)):
            if (
                undef_var not in self.configuration._data
                and undef_var not in self._configuration._data
                and undef_var not in self.j2_environment.globals.keys()
                and undef_var not in self._undefined_vars
            ):
                self._undefined_vars.append(undef_var)

        for cmd in list(self.function_calls(parsed_content)):
            self.inject_dependency(cmd)

    def get_py_tasklet_code(self, path):
        user_code = ""
        with open(path) as fh:
            user_code = fh.read().split("\n")
            if user_code[0].startswith("#!"):
                del user_code[0]
            task_code = "{0}\n{1}".format(
                "from jinjamator.task.python import PythonTask\n\
import sys,os\n\
from jinjamator.plugin_loader.content import task_init_pluginloader\n\
class jinjaTask(PythonTask):\n  def __run__(self):\n    task_init_pluginloader(self,globals())\n".format(
                    self.task_base_dir
                ),
                "\n".join(["    " + s for s in user_code]),
            )
        return task_code

    def inject_dependency(self, cmd):
        try:
            var_dependencies = self._plugin_ldr._filters.get(
                cmd, print
            ).__kwdefaults__.get("_requires", [])
            if isinstance(var_dependencies, types.FunctionType):
                for dep_var in var_dependencies():
                    if dep_var not in self._undefined_vars:
                        self._undefined_vars.append(dep_var)
            if isinstance(var_dependencies, types.list):
                for dep_var in var_dependencies:
                    if dep_var not in self._undefined_vars:
                        self._undefined_vars.append(dep_var)
        except AttributeError:
            pass

    def analyze_py_tasklet(self, tasklet):
        tasklet_code = self.get_py_tasklet_code(tasklet)
        errors = StringIO()
        warnings = StringIO()
        reporter = pyflakes_reporter(warnings, errors)
        pyflakes_check(tasklet_code, self.task_base_dir, reporter)
        undefined_vars = re.findall(
            r"(?<=undefined name ')(\S+)'\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
            warnings.getvalue(),
            re.MULTILINE,
        )
        code_lines = tasklet_code.split("\n")

        for undef_var in undefined_vars:
            code_line = code_lines[int(undef_var[1]) - 1][int(undef_var[2]) :]
            res = re.match(r"(.*)[\(|\ ].*", code_line)
            if res:
                cmd = res.group(1)
                self.inject_dependency(cmd)
            if (
                undef_var[0] not in self.configuration._data
                and undef_var[0] not in self.j2_environment.globals.keys()
                and undef_var[0] not in self._undefined_vars
            ):
                self._undefined_vars.append(undef_var[0])

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
            return False
        if var_name == "best_effort":
            self.configuration["best_effort"] = False
            return False
        if self._configuration["task_run_mode"] == "background":
            raise KeyError(
                "undefined variable found {0} and running in background -> cannot proceed".format(
                    var_name
                )
            )
        elif self._configuration["task_run_mode"] == "interactive":
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
            raise JinjamatorTaskRunException(
                "run mode {0} not implemented".format(
                    self._configuration["task_run_mode"]
                )
            )

        return self.configuration[var_name]

    def enhance_schema(self, obj, name="root"):
        title = ""
        name = str(name)
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

        try:
            with open(path, "r") as stream:
                try:
                    raw_data = stream.read()

                    environment = jinja2.Environment(extensions=["jinja2.ext.do"])
                    environment = self._plugin_ldr.j2_load_plugins(environment)
                    parsed_data = environment.from_string(raw_data).render(
                        self.configuration._data
                    )
                    # final_data=yaml.safe_load(parsed_data)
                    final_data = dotty(yaml.safe_load(parsed_data))

                    for schema_extension in self._schema_extensions:
                        self._log.error("DEPRECATED")
                        for key, value in schema_extension["data"].items():
                            # self._log.debug(key)
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
                    self._log.debug(parsed_data)
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

        schema_settings = self.load_schema_yaml(self.task_base_dir + "/schema.yaml")
        schema_template = self.configuration._data.get("wizard_template", "multistep")
        if schema_template in ["simple", "multistep"]:
            schema = self.load_schema_yaml(
                f"{os.path.dirname(__file__)}/schema/{schema_template}.yaml"
            )

        undefined_vars = self.get_undefined_task_variables()

        if "post_render" in schema_settings:
            schema["post_render"] = schema_settings["post_render"]
        if "view" in schema_settings:
            schema["view"] = schema_settings["view"]
            if not "wizard" in schema["view"]:
                schema["view"]["wizard"] = tree()

        tmp = copy.deepcopy(self.configuration._data)

        # self._log.debug(tmp)
        # self._log.debug(self._default_values)

        diff = dictdiffer.diff(self._default_values, tmp)
        # fix dictdiffer bug by iterating over diff????
        for item in diff:
            pass

        external_vars = dictdiffer.patch(diff, tree())

        diff = dictdiffer.diff(external_vars, tmp)
        self._default_values = dictdiffer.patch(diff, tmp)

        for var in undefined_vars:
            if not var in schema["schema"]["properties"]:
                schema["schema"]["properties"][var] = {}
            if not var in schema["options"]["fields"]:
                schema["options"]["fields"][var] = {}
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
            if not var in schema["schema"]["properties"]:
                schema["schema"]["properties"][var] = {}
            if not var in schema["options"]["fields"]:
                schema["options"]["fields"][var] = {}

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

        if self._default_values:
            builder = SchemaBuilder()
            builder.add_object(self._default_values)
            m = Merger(
                [(list, ["append"]), (dict, ["merge"])], ["override"], ["override"]
            )

            for k, v in builder.to_schema()["properties"].items():
                schema["schema"]["properties"][k] = v
                schema["options"]["fields"][k] = {}
                schema["schema"]["properties"][k]["default"] = self._default_values[k]
                if self._default_values[k]:
                    schema["schema"]["properties"][k]["required"] = True
                if "pass" in k:
                    schema["schema"]["properties"][k]["format"] = "password"
                # schema["schema"]["properties"][k]["required"] = True
                schema["view"]["wizard"]["bindings"][k] = 2
                schema["data"][k] = self._default_values[k]
                enhanced = self.enhance_schema(self._default_values[k], k)
                m.merge(schema["schema"]["properties"][k], enhanced)

        m = Merger(
            [(list, ["override"]), (dict, ["merge"])], ["override"], ["override"]
        )

        for key in schema_settings:
            if key in ["post_render", "view"]:
                continue
            if key not in schema["schema"]["properties"]:
                schema["schema"]["properties"][key] = {}
            m.merge(
                schema["schema"]["properties"][key],
                schema_settings[key].get("schema", {}),
            )

            if key not in schema["options"]["fields"]:
                schema["options"]["fields"][key] = {}
            m.merge(
                schema["options"]["fields"][key],
                schema_settings[key].get("options", {}),
            )

            schema["view"]["wizard"]["bindings"][key] = schema_settings[key].get(
                "form_step", 1
            )

            if "pass" in key:
                schema["schema"]["properties"][key]["format"] = "password"

            try:
                schema["data"][key] = schema_settings[key]["data"]
            except KeyError:
                pass

            try:
                schema["schema"]["dependencies"][key] = schema_settings[key][
                    "dependencies"
                ]
            except KeyError:
                pass
        # self._log.debug(pformat(schema))
        return schema

    def handle_uploaded_files(self, file_upload_var_name):
        if self._configuration["task_run_mode"] != "background":
            return None

        target_dir = os.path.join(
            self._configuration.get("jinjamator_user_directory", tempfile.gettempdir()),
            "logs",
            self._configuration.get("jinjamator_job_id"),
            "files",
        )
        os.makedirs(target_dir, exist_ok=True)
        upload_result = self.configuration[file_upload_var_name]
        filelist = []
        for cfg in upload_result:
            filename = cfg["name"]
            if os.path.isfile(cfg["filesystem_path"]):
                dirname = os.path.dirname(cfg["filesystem_path"])
                if dirname != self._configuration["uploads_folder"]:
                    self._log.error(
                        f"{dirname} is not equal uploads_folder {self._configuration['uploads_folder']} -> skipping"
                    )
                    continue
                dst_filename = f"{target_dir}/{filename}"
                self._log.debug(
                    f"Moving file {cfg['filesystem_path']} to {dst_filename}"
                )
                src_fh = open(cfg["filesystem_path"], "rb")
                dst_fh = open(dst_filename, "wb")
                while True:
                    buffer = src_fh.read(1000000)
                    if not buffer:
                        break
                    dst_fh.write(buffer)
                src_fh.close()
                dst_fh.close()
                os.unlink(cfg["filesystem_path"])
                filelist.append(dst_filename)
            else:
                self._log.error(f"cannot find uploaded file {filename} -> skipping")
        self.configuration[file_upload_var_name] = filelist

    def run(self):
        if len(self._undefined_vars) > 0:
            if self._configuration["task_run_mode"] == "background":
                self._log.error(
                    f"cannot run task because of undefined variables: {self._undefined_vars}"
                )
                raise JinjamatorTaskRunException(
                    f"cannot run task because of undefined variables: {self._undefined_vars}"
                )
            else:
                for var in self._undefined_vars:
                    self.handle_undefined_var(var)
        tmp = self.get_jsonform_schema()

        schema = tmp["schema"]
        options = tmp.get("options", {})
        for var_name in options.get("fields", {}):
            if options["fields"][var_name].get("type") == "upload":
                self.handle_uploaded_files(var_name)
        # del schema["properties"]["custom_parameters"]
        # del schema["properties"]["output_plugin"]
        # del schema["properties"]["task"]

        # validate_jsonschema(instance=self.configuration._data, schema=schema)
        # validate_jsonschema(instance=self.configuration._data, schema=self._output_plugin.get_json_schema(self.configuration._data)['schema'])
        results = []
        to_process = copy.copy(self._tasklets)
        for tasklet in self._tasklets:
            # self._plugin_ldr = ContentPluginLoader(self)
            # for content_plugin_dir in self._configuration.get(
            #     "global_content_plugins_base_dirs", []
            # ):
            #     self._plugin_ldr.load(f"{content_plugin_dir}")
            # if os.path.isdir(self._configuration["taskdir"] + "/plugins/content"):
            #     self._log.debug(
            #         "found task plugins directory "
            #         + self._configuration["taskdir"]
            #         + "/plugins/content"
            #     )
            #     self._plugin_ldr.load(
            #         self._configuration["taskdir"] + "/plugins/content"
            #     )

            self._current_tasklet = tasklet
            retval = ""

            self._log.debug(
                "running with dataset: \n{0}".format(
                    json.dumps(redact(deepcopy(self.configuration._data))[1], indent=2)
                )
            )
            if tasklet.endswith("j2"):
                try:
                    template_string = ""
                    with open(tasklet) as fh:
                        tmp = fh.read().split("\n")
                        try:
                            if tmp[0][:2] == "#!":
                                del tmp[0]
                        except IndexError:
                            pass
                        template_string = "\n".join(tmp)

                    t = self.j2_environment.from_string(template_string)
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

                module = import_code(task_code, tasklet[:-3].replace("/", "."))
                for k, v in iteritems(self.configuration._data):
                    setattr(module, k, v)

                setattr(module, "__file__", tasklet)
                setattr(module.jinjaTask, "parent", self)
                setattr(module.jinjaTask, "configuration", self.configuration._data)
                setattr(module.jinjaTask, "_configuration", self._configuration._data)
                setattr(module, "__code__", task_code)

                module._log = self._log
                try:
                    retval = module.jinjaTask().__run__()
                except Exception as e:
                    _, _, tb = sys.exc_info()
                    error_text = ""
                    code_to_show = ""
                    for filename, lineno, funname, line in reversed(
                        traceback.extract_tb(tb)
                    ):
                        if filename == "<string>":
                            filename = tasklet
                        if filename == tasklet and funname == "__run__":
                            try:
                                code_to_show = (
                                    "[ line "
                                    + str(lineno - 7)
                                    + " ] "
                                    + task_code.split("\n")[lineno - 1]
                                )
                                error_text += f"{e}\n{filename}:{lineno -7}, in {funname}\n    {line}\n {code_to_show}\n\n"
                            except Exception as inner_e:
                                self._log.debug(
                                    f"cannot show code -> this is a bug \n{inner_e }\n task_code: {task_code}\nlineno: {lineno}"
                                )
                        else:
                            error_text += (
                                f"{e}\n{filename}:{lineno}, in {funname}\n    {line}\n"
                            )

                    self._log.error(error_text)

                    if self.configuration.get("best_effort"):
                        continue
                    else:
                        to_process.pop(0)
                        skipped = []
                        for path in to_process:
                            skipped.append(os.path.basename(path))
                        results.append(
                            {
                                "tasklet_path": tasklet,
                                "result": "",
                                "status": "error",
                                "error": error_text,
                                "skipped": skipped,
                            }
                        )
                        raise TaskletFailed(
                            results,
                            f"tasklet {tasklet} has failed and best_effort is not defined -> exiting",
                        )

            else:
                raise ValueError(
                    f"tasklet {tasklet} has file extension which is not supported"
                )

            self._output_plugin.init_plugin_params()
            self._output_plugin.connect()
            self._output_plugin.process(
                retval, template_path=tasklet, current_data=self.configuration
            )

            results.append(
                {
                    "tasklet_path": tasklet,
                    "result": retval,
                    "status": "ok",
                    "error": "",
                    "skipped": [],
                }
            )
            to_process.pop(0)
            if self._configuration["task_run_mode"] == "background":
                self._log.tasklet_result(
                    "{0}".format(retval)
                )  # this submits the result via celery
        return results
