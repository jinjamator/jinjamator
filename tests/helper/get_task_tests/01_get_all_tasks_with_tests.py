from glob import glob
import os

retval = []
for base_dir in jm.environment.jinjamator_global_tasks_base_dirs():
    for test in glob(os.path.join(base_dir, "**", ".tests", "*.py"), recursive=True):
        retval.append(test)
    for test in glob(os.path.join(base_dir, "**", ".tests", "*.j2"), recursive=True):
        retval.append(test)

return retval
