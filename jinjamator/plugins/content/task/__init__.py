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


def run(path, task_data=False, **kwargs):
    """calls another jinjamator task"""

    parent_data = copy.deepcopy(self._parent.configuration._data)

    output_plugin = (
        kwargs.get("output_plugin", False)
        or parent_data.get("output_plugin", False)
        or "console"
    )

    task = JinjamatorTask(parent_data.get("task_run_mode"))

    if parent_data.get("task_run_mode") == "background":
        backup = task._log.handlers[1].formatter._task
        task.self._parent_tasklet = backup._current_tasklet
        task.self._parent_task_id = id(backup)
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
    # if not os.path.isabs(path):
    if os.path.isfile(self._parent.task_base_dir):
        my_parent = os.path.dirname(self._parent.task_base_dir)
    else:
        my_parent = self._parent.task_base_dir
    #     my_path = os.path.join(my_parent,path)
    #     if os.path.isfile(my_path):
    #         my_path = os.path.dirname(my_path)

    task.configuration["global_tasks_base_dirs"].insert(0, my_parent)

    task.load(path)

    task.load_output_plugin(
        output_plugin, task.configuration.get("global_output_plugins_base_dirs")
    )
    retval = task.run()
    if parent_data.get("task_run_mode") == "background":
        task._log.handlers[1].formatter._task = backup
        task.self._parent_tasklet = backup.self._parent_tasklet

    del task
    return retval
