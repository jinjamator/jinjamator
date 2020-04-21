from flask_restx import fields
from jinjamator.daemon.api.restx import api


site = api.model(
    "site",
    {
        "id": fields.String(required=True, description="Generated ID of site"),
        "name": fields.String(required=True, description="Generated name of site"),
    },
)


environment = api.model(
    "environment",
    {
        "id": fields.String(required=True, description="Generated ID of environment"),
        "name": fields.String(required=True, description="Name of environment"),
        "path": fields.String(required=True, description="Path to environment"),
        "sites": fields.List(fields.Nested(site)),
    },
)

environments = api.model(
    "List of environments", {"environments": fields.List(fields.Nested(environment))}
)

task_info = api.model(
    "task_info",
    {
        "id": fields.String(required=True, description="Generated ID of task"),
        "path": fields.String(
            required=True, description="Relative task path to base_dir"
        ),
        "base_dir": fields.String(
            required=True, description="Basedir where task was found"
        ),
        "description": fields.String(required=True, description="Description of task"),
    },
)

tasks = api.model("tasks_object", {"tasks": fields.List(fields.Nested(task_info))})

job_brief = api.model(
    "job_object",
    {
        "job": fields.Nested(
            api.model(
                "job_info",
                {
                    "number": fields.String(
                        required=True, description="Job number generated by Celery"
                    ),
                    "id": fields.String(
                        required=True, description="Task ID generated by Jinjamator"
                    ),
                    "state": fields.String(required=True, description="Status of job."),
                    "date_done": fields.String(
                        required=True, description="Finishing Time of Job"
                    ),
                    "date_start": fields.String(
                        required=True, description="Start Time of Job"
                    ),
                    "date_scheduled": fields.String(
                        required=True,
                        description="Time when jinjamator enqueued the Job",
                    ),
                    "task": fields.String(
                        required=True,
                        description="Relative path to task which will be, or has been executed",
                    ),
                },
            )
        )
    },
)
