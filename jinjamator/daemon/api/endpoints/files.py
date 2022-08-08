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
import glob
import os
import xxhash
from werkzeug.utils import secure_filename
import magic


log = logging.getLogger()

ns = api.namespace(
    "files", description="Operations related to jinjamator file up and downloads"
)


@ns.route("/upload")
@api.doc(
    params={"Authorization": {"in": "header", "description": "A valid access token"}}
)
class FileUpload(Resource):
    @api.expect(upload_parser, validate=True)
    @require_role(role=None)
    def post(self):
        """
        Accepts a single file.
        """
        retval = []
        args = upload_parser.parse_args(request)
        files = request.files.getlist("files")
        base_dir = os.path.join(app.config["UPLOADS_FOLDER"])
        os.makedirs(base_dir, exist_ok=True)
        for uploaded_file in files:
            data = uploaded_file.read()
            digest = xxhash.xxh128(data).hexdigest()
            file_path = os.path.join(base_dir, secure_filename(digest))
            with open(file_path, "wb") as fh:
                fh.write(data)

            mime_type = magic.from_file(file_path, mime=True)
            retval.append(
                {
                    "name": uploaded_file.filename,
                    "type": mime_type,
                    "filesystem_path": file_path,
                    "size": os.path.getsize(file_path),
                }
            )
        return {"files": retval}


@ns.route("/download/<job_id>/<file_name>")
@api.doc(
    params={"Authorization": {"in": "header", "description": "A valid access token"}}
)
class FileDownload(Resource):
    @api.doc("Download a file from job")
    @require_role(role=None)
    def get(self, job_id, file_name):
        """
        Downloads a single file which is attached to a job.
        """

        files_base_dir = os.path.join(
            app.config["JINJAMATOR_USER_DIRECTORY"], "logs", job_id, "files"
        )

        return send_from_directory(files_base_dir, file_name, as_attachment=True)
