from flask_restx import reqparse
from jinjamator.daemon.api.endpoints.environments import available_environments
from jinjamator.daemon.api.inputs import task_data
from werkzeug.datastructures import FileStorage

import logging

log = logging.getLogger()

task_arguments = reqparse.RequestParser()
task_arguments.add_argument(
    "schema-type",
    type=str,
    required=False,
    default="full",
    choices=["schema", "options", "view", "data", "full"],
    help="Select which subpart of the schema should be returned",
)

task_arguments.add_argument(
    "preload-data", type=task_data, required=False, help="preload data into schema"
)


job_arguments = reqparse.RequestParser()
job_arguments.add_argument(
    "log-level",
    type=str,
    required=False,
    default="DEBUG",
    choices=["TASKLET_RESULT", "INFO", "WARNING", "ERROR", "DEBUG"],
    help="Set the upper loglevel limit for the log entries returned",
)

upload_parser = reqparse.RequestParser()
upload_parser.add_argument("files", location="files", type=FileStorage, required=True)


aaa_login_get = reqparse.RequestParser()
aaa_login_get.add_argument(
    "username",
    type=str,
    required=False,
    help="Your Username (for local login providers only)",
)
aaa_login_get.add_argument(
    "password",
    type=str,
    required=False,
    help="Your Password (for local login providers only)",
)
