from glob import glob
import os

retval = []
for base_dir in jm.environment.jinjamator_global_tasks_base_dirs():
    for test in glob(os.path.join(base_dir, "**", ".tests", "*.py"), recursive=True):
        if self.configuration.get("task_string"):
            if self.configuration.get("task_string") in test:
                retval.append(test)
            else:
                log.info("Skipped test due to task-string filter: " + test)
        else:
            retval.append(test)
    for test in glob(os.path.join(base_dir, "**", ".tests", "*.j2"), recursive=True):
        if self.configuration.get("task_string"):
            if self.configuration.get("task_string") in test:
                retval.append(test)
            else:
                log.info("Skipped test due to task-string filter: " + test)
        else:
            retval.append(test)

return retval
