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
from jinjamator.daemon import celery
from jinjamator.task.celery.loghandler import CeleryLogHandler, CeleryLogFormatter
from jinjamator.task import TaskletFailed
from copy import deepcopy
import hashlib
import math
import random

from jinjamator.task import JinjamatorTaskRunException

def generate_debugger_pw(pw_len) :
    string = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-_!'
    OTP = ""
    length = len(string)
    for i in range(pw_len) :
        OTP += string[math.floor(random.random() * length)]
    return OTP

@celery.task(bind=True)
def run_jinjamator_task(self, path, data, output_plugin, user_id, username, debugger_cfg={}):
    """
    Jinjamator Celery Task runner.
    """

    self.update_state(
        state="PROGRESS",
        meta={
            "status": "setting up jinjamator task run",
            "configuration": {"root_task_path": path, "created_by_user_id": user_id},
        },
    )

    formatter = CeleryLogFormatter()
    log_handler = CeleryLogHandler()
    formatter.created_by_user_id = user_id
    log_handler.created_by_user_id = user_id
    log_handler.setLevel(logging.DEBUG)
    log_handler.setFormatter(formatter)

    log_handler.set_celery_task(self)

    log_handler.formatter.set_root_task_path(path)

    # if "jinjamator_pre_run_tasks" in data:
    #     for pre_run_task in data["jinjamator_pre_run_tasks"]:

    #         task = JinjamatorTask()
    #         task._configuration._data["jinjamator_job_id"] = self.request.id
    #         log_handler.formatter.set_jinjamator_task(task)
    #         task._scheduler = self
    #         task._log.addHandler(log_handler)
    #         task._log.setLevel(logging.DEBUG)
    #         if "output_plugin" in pre_run_task["task"]:
    #             task.load_output_plugin(pre_run_task["task"]["output_plugin"])
    #         else:
    #             task.load_output_plugin("console")
    #         task.configuration.merge_dict(pre_run_task["task"]["data"])
    #         task._configuration.merge_dict(
    #             celery.conf["jinjamator_private_configuration"]
    #         )

    #         task.configuration.merge_dict(deepcopy(data))

    #         task.load(pre_run_task["task"]["path"])
    #         task._log.info(
    #             "running pre run task {}".format(pre_run_task["task"]["path"])
    #         )
    #         if not task.run():
    #             raise Exception("task failed")
    #         task._log.handlers.remove(log_handler)
    #         log_handler._task = None
    #         del task

    self.update_state(
        state="PROGRESS",
        meta={
            "status": "running main task",
            "configuration": {"root_task_path": path, "created_by_user_id": user_id},
        },
    )

    task = JinjamatorTask()
    task._configuration._data["jinjamator_job_id"] = self.request.id
    task._configuration._data["root_task_path"]=path
    task._configuration._data["created_by_user_id"]=user_id
    task._configuration._data["created_by_username"]=username
    

    task._scheduler = self
    log_handler.formatter.set_jinjamator_task(task)
    task._log.setLevel(logging.DEBUG)
    task._log.addHandler(log_handler)

    task.load_output_plugin(
        output_plugin,
        celery.conf["jinjamator_private_configuration"][
            "global_output_plugins_base_dirs"
        ],
    )

    task._configuration.merge_dict(celery.conf["jinjamator_private_configuration"])

    task.configuration.merge_dict(data)
    
    if debugger_cfg.get('enabled'):
        debugger_pw=generate_debugger_pw(64)
        task._configuration._data["debugger_hash"]=hashlib.sha512(debugger_pw.encode('utf-8')).hexdigest()
        task._celery=self
        self.update_state(
            state="SETUP_DEBUGGER",
            meta={
                "status": "setting up debugger",
                "configuration": {"root_task_path": path, "created_by_user_id": user_id, "debugger_password": debugger_pw},
            },
        )

    task.load(path)
    

    
    try:
        task.run()
    except TaskletFailed as e:
        task._log.error(e)
        raise JinjamatorTaskRunException("task failed")

    return {
        "status": "finished task",
        "stdout": task._stdout.getvalue(),
        "log": log_handler.contents,
    }
