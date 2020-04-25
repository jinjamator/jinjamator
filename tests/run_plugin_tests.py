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

test_paths = glob(
    f"{os.path.dirname(__file__)}{os.path.sep}plugins/{os.path.sep}**{os.path.sep}*.py",
    recursive=True,
) + glob(
    f"{os.path.dirname(__file__)}{os.path.sep}plugins/{os.path.sep}**{os.path.sep}*.j2",
    recursive=True,
)


for tasklet_path in test_paths:
    task_path = os.path.dirname(tasklet_path)
    if task_path not in tests:
        tests.append(task_path)
failed = 0

for test in tests:
    print(f"running test {test}:")
    try:
        for tasklet_path, tasklet_return_value in task.run(
            test, output_plugin="null"
        ).items():
            print(f"\t{os.path.basename(tasklet_path)}", end=" ")
            if "content" in tasklet_path:
                if tasklet_return_value == "OK":
                    print(Fore.GREEN + str(tasklet_return_value))
                else:
                    print(Fore.RED + str(tasklet_return_value))
                    failed += 1
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

print(f"Failed tests: {failed}")
if failed:
    sys.exit(1)
else:
    sys.exit(0)
