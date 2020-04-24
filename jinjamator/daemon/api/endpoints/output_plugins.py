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
class PluginsCollection(Resource):
    def get(self):
        """
        Returns a list of all output plugins with it's full alpacajs form schema.
        """
        return available_output_plugins


@ns.route("/<plugin_name>")
class PluginInfo(Resource):
    @api.response(404, "Plugin not found Error")
    @api.response(200, "Success")
    def get(self, plugin_name):
        """
        Returns information about a output plugin with it's full alpacajs form schema.
        """

        retval = available_output_plugins_by_name.get(plugin_name)
        if retval:
            return retval
        else:
            abort(404, f"Plugin {plugin_name} not found")
