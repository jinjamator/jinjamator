import logging

from flask import request, jsonify
from flask_restx import Resource, abort
from jinjamator.daemon.api.serializers import job_brief
from jinjamator.daemon.api.restx import api
from jinjamator.external.celery.backends.database.models import Task as DB_Job, JobLog
from jinjamator.daemon.database import db
from jinjamator.daemon.api.parsers import job_arguments
from flask import current_app as app

from sqlalchemy import select, and_, or_, exc
import glob
import os
import xxhash
import json
from glob import glob
from uuid import UUID

log = logging.getLogger()

ns = api.namespace("jobs", description="Operations related to jinjamator jobs")
available_environments = []
preload_defaults_from_site_choices = []
site_path_by_name = {}


@ns.route("/")
class JobCollection(Resource):
    @api.marshal_list_with(job_brief)
    def get(self):
        """
        Returns a list of all jobs.
        """
        response = []
        try:
            rs = db.session.execute(
                select(
                    [
                        DB_Job.id,
                        DB_Job.task_id,
                        DB_Job.status,
                        DB_Job.date_done,
                        DB_Job.date_start,
                        DB_Job.date_scheduled,
                        DB_Job.jinjamator_task,
                    ]
                ).order_by(DB_Job.id.desc())
            )
        except exc.SQLAlchemyError as e:
            log.error(e)
            return response
        for job in rs.fetchall():
            response.append(
                {
                    "job": {
                        "number": str(job.id),
                        "id": str(job.task_id),
                        "state": str(job.status),
                        "date_done": str(job.date_done),
                        "date_start": str(job.date_start),
                        "date_scheduled": str(job.date_scheduled),
                        "task": str(job.jinjamator_task),
                    }
                }
            )

        return response


@ns.route("/<job_id>")
@api.doc(
    params={"job_id": "The ID returned by task create operation. (UUID V4 format)"}
)
class Job(Resource):
    @api.expect(job_arguments)
    @api.response(404, "Task not found Error")
    @api.response(400, "Task ID not in UUID V4 format")
    @api.response(200, "Success")
    def get(self, job_id):
        """
        Returns detailed information about a job, including a full debug log.
        """
        try:
            UUID(job_id, version=4)
        except ValueError:
            abort(400, "Task ID not in UUID V4 format")

        args = job_arguments.parse_args(request)
        log_level = args.get("log-level", "DEBUG")
        try:
            job = db.session.query(DB_Job).filter(DB_Job.task_id == job_id).all()[0]
            response = {
                "id": job.task_id,
                "state": job.status,
                "jinjamator_task": job.jinjamator_task,
                "log": [],
                "files": [],
            }
        except exc.SQLAlchemyError as e:
            log.error(e)
            abort(404, f"Job ID {job_id} not found")

        log_level_filter = JobLog.level.is_("TASKLET_RESULT")
        if log_level in ["INFO", "WARNING", "ERROR", "DEBUG"]:
            log_level_filter = or_(log_level_filter, JobLog.level.is_("INFO"))
        if log_level in ["WARNING", "ERROR", "DEBUG"]:
            log_level_filter = or_(log_level_filter, JobLog.level.is_("WARNING"))
        if log_level in ["ERROR", "DEBUG"]:
            log_level_filter = or_(log_level_filter, JobLog.level.is_("ERROR"))
        if log_level in ["DEBUG"]:
            log_level_filter = or_(log_level_filter, JobLog.level.is_("DEBUG"))

        for row in (
            db.session.query(JobLog)
            .filter(and_(JobLog.task_id == job_id, log_level_filter))
            .order_by(JobLog.timestamp)
            .all()
        ):
            response["log"].append(
                {
                    str(row.timestamp): {
                        "configuration": json.loads(row.configuration),
                        "current_task": row.current_task,
                        "current_task_id": row.current_task_id,
                        "current_tasklet": row.current_tasklet,
                        "level": row.level,
                        "message": row.message,
                        "parent_task_id": row.parent_task_id,
                        "parent_tasklet": row.parent_tasklet,
                        "stdout": row.stdout,
                    }
                }
            )
        files_base_dir = os.path.join(
            app.config["JINJAMATOR_USER_DIRECTORY"], "logs", job_id, "files"
        )
        for file_path in glob(os.path.join(files_base_dir, "*")):
            if os.path.isfile(file_path):
                response["files"].append(file_path.replace(files_base_dir, "")[1:])

        return response
