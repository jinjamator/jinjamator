import logging

from flask import request, send_from_directory
from flask_restx import Resource
from jinjamator.daemon.api.serializers import environments
from jinjamator.daemon.api.restx import api
from jinjamator.daemon.api.parsers import upload_parser
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
class FileUpload(Resource):
    @api.expect(upload_parser, validate=True)
    def post(self):
        """
        Accepts a single file.
        """
        retval = []
        args = upload_parser.parse_args(request)
        files = request.files.getlist("files")
        base_dir = os.path.join(app.config["UPLOAD_FOLDER"], "uploads")
        for uploaded_file in files:
            file_path = os.path.join(base_dir, secure_filename(uploaded_file.filename))
            uploaded_file.save(file_path)
            mime_type = magic.from_file(file_path, mime=True)
            retval.append(
                {
                    "name": uploaded_file.filename,
                    "type": mime_type,
                    "filesystem_path": file_path,
                    "size": os.path.getsize(file_path),
                }
            )
        return retval


@ns.route("/download/<job_id>/<file_name>")
class FileUpload(Resource):
    @api.doc("Download a file from job")
    def get(self, job_id, file_name):
        """
        Downloads a single file.
        """

        files_base_dir = os.path.join(
            app.config["JINJAMATOR_USER_DIRECTORY"], "logs", job_id, "files"
        )

        return send_from_directory(files_base_dir, file_name, as_attachment=True)
