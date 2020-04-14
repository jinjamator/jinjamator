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

from . import app
from jinjamator.task.celery import run_jinjamator_task
from jinjamator.task import JinjamatorTask
from celery.result import ResultBase
import json
from flask import url_for, jsonify, request, send_from_directory, render_template
from celery import current_app
from jinjamator.external.celery.backends.database.models import Task as DB_Job
from jinjamator.external.celery.backends.database.models import JobLog

from collections import defaultdict
from time import sleep
import glob
import os
import datetime
from threading import Thread
from sqlalchemy import select
from flask_sqlalchemy import SQLAlchemy
import logging
from werkzeug.routing import PathConverter
from werkzeug.utils import secure_filename
import xxhash
import uuid
import magic


class EverythingConverter(PathConverter):
    regex = ".*?"


app.url_map.converters["everything"] = EverythingConverter


db = SQLAlchemy(app)
log = logging.getLogger()


def tree():
    return defaultdict(tree)


@app.route("/", methods=["GET", "POST"])
def index():
    global log
    log.error(
        os.path.sep.join([os.path.dirname(__file__), "web", "static", "templates"])
    )
    return send_from_directory(
        os.path.sep.join([os.path.dirname(__file__), "web", "static", "templates"]),
        "index.html",
    )


@app.route("/api/upload", methods=["POST"])
def handle_file_upload():
    log = logging.getLogger()
    retval = []
    files = request.files.getlist("files")
    log.debug(request.form.to_dict())
    if request.form.get("environment"):
        base_dir = os.path.join(request.form.get("environment"), "jobs")
    else:
        base_dir = app.config["UPLOAD_FOLDER"]

    if request.form.get("jinjamator_job_id"):
        base_dir = os.path.join(base_dir, request.form.get("jinjamator_job_id"))
    base_dir = os.path.join(base_dir, "uploads")
    os.makedirs(base_dir, exist_ok=True)

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
        log.debug(retval)

    return jsonify({"files": retval})


@app.route("/static/<path:path>", methods=["GET"])
def get_static_content(path):
    return send_from_directory(
        os.path.sep.join([os.path.dirname(__file__), "web", "static"]), path
    )


@app.route("/api/environments", methods=["GET"])
def api_list_environments():
    response = {"environments": []}
    for directory in app.config["JINJAMATOR_ENVIRONMENTS_BASE_DIRECTORIES"]:

        for path in glob.glob("{0}/**/sites/*/".format(directory), recursive=True):
            tmp = path.split(os.path.sep)
            response["environments"].append(
                {"path": path, "name": "{}-{}".format(tmp[-4], tmp[-2])}
            )
    return jsonify(response)


@app.route("/api/tasks", methods=["GET"])
def api_list_tasks():
    response = {"tasks": []}
    for directory in app.config["JINJAMATOR_TASKS_BASE_DIRECTORIES"]:
        tasks = glob.glob("{0}/**/*.py".format(directory), recursive=True) + glob.glob(
            "{0}/**/*.j2".format(directory), recursive=True
        )
        for item in tasks:
            append = True
            for dir_chunk in os.path.dirname(item).split(os.path.sep):
                if dir_chunk.startswith("."):
                    append = False
            if append:
                dir_name = os.path.dirname(item)
                if dir_name not in response["tasks"] and os.path.isfile(
                    item
                ):  # this is not the final solution, we should filter on filetypes aswell
                    if "__pycache__" not in dir_name:
                        response["tasks"].append(dir_name)
    return jsonify(response)


@app.route("/api/tasks/<everything:path>", methods=["GET"], strict_slashes=False)
def api_get_task_info(path):

    task = JinjamatorTask()
    task._log.warning(path)
    if path.startswith("api/tasks/"):
        path = path[10:]
    if request.values:
        if request.values["environment"] != "":
            task.configuration.merge_yaml(
                "{}/defaults.yaml".format(request.values["environment"])
            )
        task.configuration.merge_dict(
            json.loads(request.values["data"]),
            dict_strategy="merge",
            list_strategy="override",
            other_types_strategy="override",
            type_conflict_strategy="override",
        )
    task.load(path)

    return jsonify(task.get_jsonform_schema())


@app.route("/api/jobs", methods=["POST"])
def api_create_job():
    data = request.get_json()
    try:
        data["output_plugin"]
    except:
        data["output_plugin"] = "console"
    try:
        data["configuration"]
    except:
        data["configuration"] = {}
        data["configuration"]["output_plugin"] = data["output_plugin"]

    try:
        for param in data["configuration"]["custom_parameters"]:
            data["configuration"][param["key"]] = param["value"]
        del data["configuration"]["custom_parameters"]
    except KeyError:
        pass
    job_id = data["configuration"].get("jinjamator_job_id", uuid.uuid4())
    job = run_jinjamator_task.apply_async(
        [data["task"], data["configuration"], data["output_plugin"]], task_id=job_id
    )

    db_job = list(db.session.query(DB_Job).filter(DB_Job.task_id == job.id))
    db_job = db_job and db_job[0]
    if not db_job:
        db_job = DB_Job(job.id)
        db_job.status = "SCHEDULED"
        db_job.configuration = data["configuration"]
        db_job.jinjamator_task = data["task"]
        db.session.add(db_job)
        db.session.flush()
        db.session.commit()

    return jsonify({"job_id": job.id})


@app.route("/api/jobs", methods=["GET"])
def api_list_jobs():

    response = []

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
    for job in rs.fetchall():
        response.append(
            {
                str(job.id): {
                    "id": job.id,
                    "task_id": job.task_id,
                    "state": job.status,
                    "date_done": job.date_done,
                    "date_start": job.date_start,
                    "date_scheduled": job.date_scheduled,
                    "task": job.jinjamator_task,
                }
            }
        )

    return jsonify(response)


@app.route("/api/jobs/<job_id>", methods=["GET", "DELETE"])
def job_status(job_id, raw=False):

    job = db.session.query(DB_Job).filter(DB_Job.task_id == job_id).all()[0]
    response = tree()
    response["id"] = job.task_id
    response["state"] = job.status
    response["jinjamator_task"] = job.jinjamator_task
    response["log"] = []
    for row in (
        db.session.query(JobLog)
        .filter(JobLog.task_id == job_id)
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
    if raw:
        return response
    else:
        return jsonify(response)


@app.route("/api/plugins/output", methods=["GET"])
def api_list_output_plugins(raw=False):
    response = []
    for file_name in os.listdir(
        "{0}/plugins/output".format(app.config["JINJAMATOR_BASE_DIRECTORY"])
    ):
        if file_name not in ["__pycache__", "__init__.py"]:
            if file_name.endswith("py"):
                response.append(file_name[:-3])
    if raw:
        return response
    else:
        return jsonify(response)


@app.route("/api/plugins/output/<plugin_name>", methods=["GET"])
def api_get_output_plugin_parameters(plugin_name):
    response = []

    if plugin_name not in api_list_output_plugins(True):  # avoid path traversal attacks
        return jsonify(response)

    try:
        with open(
            "{0}/plugins/output/{1}.py".format(
                app.config["JINJAMATOR_BASE_DIRECTORY"], plugin_name
            )
        ) as fh:
            code = fh.read()
            mod = importCode(code, "tmp")
            plug = getattr(mod, plugin_name)
            response = plug.get_json_form(request.values)

    except FileNotFoundError:
        return jsonify(response)

    return jsonify(response)
