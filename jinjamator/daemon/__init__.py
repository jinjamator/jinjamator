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

from flask import Flask, Blueprint
from jinjamator.daemon.api.restx import api
from jinjamator.daemon.api.endpoints.environments import ns as environments_namespace
from jinjamator.daemon.api.endpoints.tasks import ns as tasks_namespace

import logging
app = Flask(__name__)
log = logging.getLogger()


def configure(flask_app, configuration):
    flask_app.url_map.strict_slashes = False
    flask_app.config['SERVER_NAME'] = 'localhost:5000'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = 'list'
    flask_app.config['RESTPLUS_VALIDATE'] = True
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = False
    flask_app.config['ERROR_404_HELP'] = False
    flask_app.config["CELERY_BROKER_URL"] = configuration.get("celery_broker")
    flask_app.config["CELERY_RESULT_BACKEND"] = configuration.get("celery_result_backend")
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = configuration.get("celery_result_backend")
    flask_app.config["JINJAMATOR_BASE_DIRECTORY"] = configuration.get("jinjamator_base_directory")
    flask_app.config["UPLOAD_FOLDER"] = "/tmp"
    flask_app.config["JINJAMATOR_GLOBAL_DEFAULTS"] = configuration.get("global_defaults")
    flask_app.config["JINJAMATOR_TASKS_BASE_DIRECTORIES"] = configuration.get("global_tasks_base_dirs")
    flask_app.config["JINJAMATOR_ENVIRONMENTS_BASE_DIRECTORIES"] = configuration.get("global_environments_base_dirs")
    flask_app.config["JINJAMATOR_OUTPUT_PLUGINS_BASE_DIRS"] = configuration.get("global_output_plugins_base_dirs")
    flask_app.config["JINJAMATOR_CONTENT_PLUGINS_BASE_DIRS"] = configuration.get("global_content_plugins_base_dirs")

def initialize(flask_app, cfg):
    configure(flask_app,cfg)

    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(environments_namespace)
    api.add_namespace(tasks_namespace)
    # api.add_namespace(blog_categories_namespace)
    flask_app.register_blueprint(blueprint)

    # db.init_app(flask_app)


def run(cfg):
    initialize(app, cfg)
    log.info('>>>>> Starting development server at http://{}/api/ <<<<<'.format(app.config['SERVER_NAME']))
    app.run(debug=True, host="0.0.0.0")
