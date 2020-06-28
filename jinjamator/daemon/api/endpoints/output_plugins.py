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

from flask import request
from flask_restx import Resource
from jinjamator.daemon.api.serializers import environments
from jinjamator.daemon.api.restx import api
from jinjamator.plugin_loader.output import load_output_plugin
from flask import current_app as app
import glob
import os
import xxhash
from flask_restx import abort
from jinjamator.daemon.api.parsers import task_arguments
from jinjamator.daemon.aaa import require_role


log = logging.getLogger()

ns = api.namespace(
    "plugins/output", description="Operations related to jinjamator output plugins"
)
available_output_plugins = []
available_output_plugin_names = []
available_output_plugins_by_name = {}


class DummyTask(object):
    def __init__(self):
        self._output_plugin = None


def discover_output_plugins(app):
    """
    Discovers all output_plugins found in global_output_plugins_base_dirs.
    """

    for base_dir in app.config["JINJAMATOR_OUTPUT_PLUGINS_BASE_DIRS"]:
        for plugin_dir in glob.glob(os.path.join(base_dir, "*")):
            if os.path.isdir(plugin_dir):
                plugin_name = os.path.basename(plugin_dir)
                dummy = DummyTask()
                load_output_plugin(
                    dummy,
                    plugin_name,
                    app.config["JINJAMATOR_OUTPUT_PLUGINS_BASE_DIRS"],
                )
                current_plugin = {
                    "id": xxhash.xxh64(plugin_name).hexdigest(),
                    "path": plugin_dir,
                    "name": plugin_name,
                    "schema": dummy._output_plugin.get_json_schema(),
                }
                available_output_plugins.append(current_plugin)
                available_output_plugin_names.append(plugin_name)
                available_output_plugins_by_name[plugin_name] = current_plugin


@ns.route("/")
@api.doc(
    params={"Authorization": {"in": "header", "description": "A valid access token"}}
)
class PluginsCollection(Resource):
    @api.response(200, "Success")
    @require_role(role=None)
    def get(self):
        """
        Returns a list of all output plugins with it's full alpacajs form schema.
        """
        return available_output_plugins


@ns.route("/<plugin_name>")
@api.doc(
    params={"Authorization": {"in": "header", "description": "A valid access token"}}
)
class PluginInfo(Resource):
    @api.response(404, "Plugin not found Error")
    @api.response(200, "Success")
    @require_role(role=None)
    def get(self, plugin_name):
        """
        Returns information about a output plugin with it's full alpacajs form schema.
        """
        retval = available_output_plugins_by_name.get(plugin_name)
        if retval:
            if request.args:
                dummy = DummyTask()
                load_output_plugin(
                    dummy,
                    plugin_name,
                    app.config["JINJAMATOR_OUTPUT_PLUGINS_BASE_DIRS"],
                )
                retval["schema"] = dummy._output_plugin.get_json_schema(request.args)

                return retval
        else:
            abort(404, f"Plugin {plugin_name} not found")
