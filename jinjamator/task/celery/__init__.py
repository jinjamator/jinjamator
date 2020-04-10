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

from celery import Celery
from jinjamator.task import JinjamatorTask
import importlib
import sys
import os
from time import sleep
import collections
import logging
import json
from celery.exceptions import Ignore
from jinjamator.task.celery.loghandler import CeleryLogHandler, CeleryLogFormatter
from jinjamator.external.celery.backends.database import DatabaseBackend
from jinjamator.daemon import app
from copy import deepcopy

celery = Celery("jinjamator", broker=app.config["CELERY_BROKER_URL"])


@celery.task(
    bind=True,
    backend=DatabaseBackend(app=celery, url=app.config["CELERY_RESULT_BACKEND"]),
)
def run_jinjamator_task(self, path, data, output_plugin):
    self.update_state(
        state="PROGRESS",
        meta={
            "status": "setting up jinjamator task run",
            "configuration": {"root_task_path": path},
        },
    )

    formatter = CeleryLogFormatter()
    log_handler = CeleryLogHandler()

    log_handler.setLevel(logging.DEBUG)
    log_handler.setFormatter(formatter)
    log_handler.set_celery_task(self)

    log_handler.formatter.set_root_task_path(path)

    if "jinjamator_pre_run_tasks" in data:
        for pre_run_task in data["jinjamator_pre_run_tasks"]:

            task = JinjamatorTask()
            log_handler.formatter.set_jinjamator_task(task)
            task._scheduler = self
            task._log.addHandler(log_handler)
            task._log.setLevel(logging.DEBUG)
            if "output_plugin" in pre_run_task["task"]:
                task.load_output_plugin(pre_run_task["task"]["output_plugin"])
            else:
                task.load_output_plugin("console")
            task.configuration.merge_dict(pre_run_task["task"]["data"])
            task.configuration.merge_dict(deepcopy(data))

            task.load(pre_run_task["task"]["path"])
            task._log.info(
                "running pre run task {}".format(pre_run_task["task"]["path"])
            )
            if not task.run():
                raise Exception("task failed")
            task._log.handlers.remove(log_handler)
            log_handler._task = None
            del task

    self.update_state(
        state="PROGRESS",
        meta={"status": "running main task", "configuration": {"root_task_path": path}},
    )

    task = JinjamatorTask()
    task._scheduler = self
    log_handler.formatter.set_jinjamator_task(task)
    task._log.setLevel(logging.DEBUG)
    task._log.addHandler(log_handler)

    task.load_output_plugin(
        output_plugin, app.config["JINJAMATOR_OUTPUT_PLUGINS_BASE_DIRS"]
    )
    task.configuration.merge_dict(data)

    task.load(path)

    if not task.run():
        raise Exception("task failed")

    return {
        "status": "finished task",
        "stdout": task._stdout.getvalue(),
        "log": log_handler.contents,
    }
