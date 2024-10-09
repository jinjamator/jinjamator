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

from flask import request, jsonify, g
from flask_restx import Resource, abort
from jinjamator.daemon.api.serializers import job_brief
from jinjamator.daemon.api.restx import api
from jinjamator.external.celery.backends.database.models import Task as DB_Job, JobLog
from jinjamator.daemon.database import db
from jinjamator.daemon.api.parsers import job_arguments
from jinjamator.daemon.aaa import require_role
from jinjamator.daemon.aaa.models import User, JinjamatorRole

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
@api.doc(
    params={"Authorization": {"in": "header", "description": "A valid access token"}}
)
class JobCollection(Resource):
    @api.marshal_list_with(job_brief)
    @api.response(200, "Success")
    @require_role(role="operator")
    def get(self):
        """
        Returns a list of all jobs.
        """
        response = []
        user_roles = [role["name"] for role in g._user["roles"]]


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
                        DB_Job.created_by_user_id,
                    ]
                ).order_by(DB_Job.id.desc())
            )
        except exc.SQLAlchemyError as e:
            log.error(e)
            return response

        for job in rs.fetchall():
            user = User.query.filter(User.id == int(job.created_by_user_id)).first()           
        
            if user:
                username = str(user.username)
            else:
                username = f"deleted (id is {job.created_by_user_id})"
            allowed=False
            if "administrator" in user_roles or "tasks_all" in user_roles:
                allowed=True
            for role in user_roles:
                if f"task_{str(job.jinjamator_task)}".startswith(role):
                    allowed=True
            if allowed:
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
                            "created_by_user_id": int(job.created_by_user_id),
                            "created_by_user_name": username,
                        }
                    }
                )

        return response


@ns.route("/<job_id>")
@api.doc(
    params={
        "job_id": "The ID returned by task create operation. (UUID V4 format)",
        "Authorization": {"in": "header", "description": "A valid access token"},
    }
)
class Job(Resource):
    @api.expect(job_arguments)
    @api.response(404, "Task not found Error")
    @api.response(400, "Task ID not in UUID V4 format")
    @api.response(200, "Success")
    @require_role(role="operator")
    def get(self, job_id):
        """
        Returns detailed information about a job, including a full debug log.
        """
        try:
            UUID(job_id, version=4)
        except ValueError:
            abort(400, "Task ID not in UUID V4 format")

        # import logging
        # logging.basicConfig()
        # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

        args = job_arguments.parse_args(request)
        log_level = args.get("log-level", "DEBUG")
        newer_than = args.get("logs-newer-than", None)
        


            
        try:
            job = db.session.query(DB_Job).filter(DB_Job.task_id == job_id).first()
            user = User.query.filter(User.id == int(job.created_by_user_id)).first()
            user_roles = [role["name"] for role in g._user["roles"]]

            allowed=False
            if "administrator" in user_roles or "tasks_all" in user_roles:
                allowed=True
            for role in user_roles:
                if f"task_{str(job.jinjamator_task)}".startswith(role):
                    allowed=True
            if not allowed:
                abort(403, f"You have no accees to {job_id}, as you have no permission for {job.jinjamator_task} ")
            response = {
                "id": job.task_id,
                "state": job.status,
                "jinjamator_task": job.jinjamator_task,
                "log": [],
                "files": [],
                "created_by_user_id": int(job.created_by_user_id),
                "created_by_user_name": str(user.username),
            }

            if "debugger" in user_roles:
                response["debugger_password"] = str(job.debugger_password)

        except exc.SQLAlchemyError as e:
            log.error(e)
            abort(404, f"Job ID {job_id} not found")

        log_level_filter = JobLog.level.is_("TASKLET_RESULT")
        log_level_filter = or_(log_level_filter, JobLog.level.is_("CONSOLE"))
        if log_level in ["INFO","WARNING", "ERROR", "DEBUG"]:
            log_level_filter = or_(log_level_filter, JobLog.level.is_("ERROR"))
        if log_level in ["INFO","WARNING", "DEBUG"]:
            log_level_filter = or_(log_level_filter, JobLog.level.is_("WARNING"))
        if log_level in ["INFO", "DEBUG"]:
            log_level_filter = or_(log_level_filter, JobLog.level.is_("INFO"))
        if log_level in ["DEBUG"]:
            log_level_filter = or_(log_level_filter, JobLog.level.is_("DEBUG"))

        if newer_than:
            log_level_filter = and_(log_level_filter,JobLog.timestamp > newer_than)


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
