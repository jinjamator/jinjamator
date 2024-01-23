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

from flask import request, send_from_directory
from flask_restx import Resource
from jinjamator.daemon.api.serializers import environments
from jinjamator.daemon.api.restx import api
from jinjamator.daemon.api.parsers import upload_parser
from jinjamator.daemon.aaa import require_role
from flask import current_app as app



log = logging.getLogger()

ns = api.namespace(
    "info", description="Operations related to jinjamator internal information"
)


@ns.route("/version")
@api.doc(
    params={"Authorization": {"in": "header", "description": "A valid access token"}}
)
class VersionInfo(Resource):
    @require_role(role=None)
    def get(self):
        """
        Get running Jinjamator version
        """
        return {"version": app.config["JINJAMATOR_VERSION"]}


