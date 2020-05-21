#!/usr/bin/env -S jinjamator -t
from glob import glob
import os, sys, logging
from colorama import init
import traceback

init()
from colorama import Fore, Style

tests = []

logger = logging.getLogger()
# logger.disabled = True

apic_url, apic_username, apic_password, ssh_host, ssh_username, ssh_password

test_paths = (
    glob(
        f"{os.path.dirname(__file__)}{os.path.sep}plugins/{os.path.sep}**{os.path.sep}*.py",
        recursive=True,
    )
    + glob(
        f"{os.path.dirname(__file__)}{os.path.sep}plugins/{os.path.sep}**{os.path.sep}*.j2",
        recursive=True,
    )
    + glob(
        f"{os.path.dirname(__file__)}{os.path.sep}api/{os.path.sep}**{os.path.sep}*.py",
        recursive=True,
    )
)

for tasklet_path in test_paths:
    task_path = os.path.dirname(tasklet_path)
    if task_path not in tests:
        tests.append(task_path)
failed = 0


container_data = task.run("helper/create_docker_container", output_plugin="null")[1][
    "result"
]

cfg = self.configuration
cfg["_container"] = container_data

for test in tests:
    print(f"running test {test}:")
    try:
        for retval in task.run(test, cfg, output_plugin="null"):
            tasklet_path = retval["tasklet_path"]
            tasklet_return_value = retval["result"]
            print(f"\t{os.path.basename(tasklet_path)}", end=" ")
            if "/content/" in tasklet_path or "/api/" in tasklet_path:
                if tasklet_return_value == "OK":
                    print(Fore.GREEN + str(tasklet_return_value))
                else:
                    print(Fore.RED + str(tasklet_return_value))
                    failed += 1
                print(Style.RESET_ALL, end="")
            elif "/output/" in tasklet_path:
                print(Fore.GREEN + "OK")
                print(Style.RESET_ALL, end="")
            else:
                print(Fore.YELLOW + "NOT IMPLEMENTED")
                print(Style.RESET_ALL, end="")

    except Exception as e:
        print(f"\t{os.path.basename(tasklet_path)}", end=" ")
        print(Fore.RED + "NOT OK")
        print(f"\t{e}")
        print(f"\t{traceback.format_exc()}")

        failed += 1
        print(Style.RESET_ALL, end="")

print(Style.RESET_ALL, end="")
print(f"Failed tests: {failed}")
if failed:
    sys.exit(1)
