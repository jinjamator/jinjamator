from flask_restx import reqparse
from jinjamator.daemon.api.endpoints.environments import available_environments
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

job_arguments = reqparse.RequestParser()
job_arguments.add_argument(
    "log-level",
    type=str,
    required=False,
    default="DEBUG",
    choices=["TASKLET_RESULT", "INFO", "WARNING", "ERROR", "DEBUG"],
    help="Set the upper loglevel limit for the log entries returned",
)
