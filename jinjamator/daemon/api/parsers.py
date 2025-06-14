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

from flask_restx import reqparse, fields, inputs
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
    choices=["TASK_SUMMARY", "TASKLET_RESULT", "INFO", "WARNING", "ERROR", "DEBUG"],
    help="Set the upper loglevel limit for the log entries returned. Selection of TASK_SUMMARY will exclusivly return the last TASK_SUMMARY.",
)

job_arguments.add_argument(
    "logs-newer-than",
    type=inputs.datetime_from_iso8601,
    required=False,
    default="1970-01-01T00:00:00.0000",
    help="Get logs created > $logs-newer-than. Expected format is ISO8601. Eg.: 1970-01-01T00:00:00.0000",
)

job_arguments.add_argument(
    "show-tasklet-results",
    type=str,
    required=False,
    default="false",
    choices=["true", "false"],
    help="Include tasklet results in logs output.",
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
