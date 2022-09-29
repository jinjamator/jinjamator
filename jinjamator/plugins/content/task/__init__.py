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

import copy
import os
from jinjamator.task import JinjamatorTask
import logging


def run(path, task_data=False, **kwargs):
    """calls another jinjamator task"""

    if path == "../":
        tmp = _jinjamator.task_base_dir.split(os.path.sep)
        if tmp[0] == "":
            tmp[0] = os.path.sep
        path = os.path.join(*tmp[:-1])

    parent_data = copy.deepcopy(_jinjamator.configuration._data)
    parent_private_data = copy.deepcopy(_jinjamator._configuration._data)

    output_plugin = (
        kwargs.get("output_plugin", False)
        or parent_data.get("output_plugin", False)
        or "console"
    )

    task = JinjamatorTask(parent_private_data.get("task_run_mode"))
    task._configuration.merge_dict(parent_private_data)
    task._parent_tasklet = _jinjamator._current_tasklet

    if parent_private_data.get("task_run_mode") == "background":
        backup = task._log.handlers[1].formatter._task
        task._parent_tasklet = backup._current_tasklet
        task._parent_task_id = id(backup)
        task._log.handlers[1].formatter._task = task
    if task_data:
        task.configuration.merge_dict(
            task_data,
            dict_strategy="merge",
            list_strategy="override",
            other_types_strategy="override",
            type_conflict_strategy="override",
        )
    else:
        task.configuration.merge_dict(parent_data)

    task.configuration["output_plugin"] = output_plugin
    task._configuration["global_tasks_base_dirs"].insert(0, _jinjamator.task_base_dir)

    try:
        task.load(path)
    except Exception as e:
        logging.error(e)
        raise e

    task.load_output_plugin(
        output_plugin, task._configuration.get("global_output_plugins_base_dirs")
    )
    try:
        retval = task.run()
    except Exception as e:
        logging.error(e)
        raise e

    if parent_private_data.get("task_run_mode") == "background":
        task._log.handlers[1].formatter._task = backup
        task._parent_tasklet = backup._parent_tasklet
    del task
    return retval


def directory():
    return _jinjamator._configuration.get("taskdir", None)
