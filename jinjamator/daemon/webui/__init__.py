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

import os
from flask import send_from_directory, Blueprint
import logging
from jinjamator.daemon.aaa import aaa_providers

webui = Blueprint("webui", __name__, url_prefix="/")
log = logging.getLogger()


@webui.route("/index.html", methods=["GET"])
@webui.route("/", methods=["GET"])
def index():
    """
    Just send static index.html
    """
    return send_from_directory(
        os.path.sep.join([os.path.dirname(__file__), "static"]), "index.html"
    )


@webui.route("/login.html", methods=["GET"])
def login():
    """
    Just send static login.html
    """
    return send_from_directory(
        os.path.sep.join([os.path.dirname(__file__), "static"]), "login.html"
    )
