#!/usr/bin/env -S jinjamator -t
from glob import glob
import os, sys, logging
from colorama import init
import traceback
from tempfile import mkstemp

init()
from colorama import Fore, Style

tests = []

log_file = mkstemp(suffix=".log", prefix="jinjamtor_tests_", text=True)[1]

logger = logging.getLogger()
fh = logging.FileHandler(log_file)
logger.handlers.pop()
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)

print(f"Logfile for this run is {log_file}")

# logger.disabled = True

# apic_url, apic_username, apic_password, ssh_host, ssh_username, ssh_password

test_paths = []
cfg = self.configuration

if "plugins" in run_tests or "all" in run_tests:
    print("adding plugin tests to test list")
    test_paths += glob(
        f"{os.path.dirname(__file__)}{os.path.sep}plugins/{os.path.sep}**{os.path.sep}*.py",
        recursive=True,
    ) + glob(
        f"{os.path.dirname(__file__)}{os.path.sep}plugins/{os.path.sep}**{os.path.sep}*.j2",
        recursive=True,
    )


if "api" in run_tests or "all" in run_tests:
    print("adding api tests to test list")
    test_paths += glob(
        f"{os.path.dirname(__file__)}{os.path.sep}api/{os.path.sep}**{os.path.sep}*.py",
        recursive=True,
    )
    print("creating test container for api tests")
    container_data = task.run("helper/create_docker_container", output_plugin="null")[
        1
    ]["result"]
    cfg["_container"] = container_data
    log.info("done creating test container for api tests")


if "tasks" in run_tests or "all" in run_tests:
    print("adding task unit tests to test list")
    test_paths += task.run("helper/get_task_tests", output_plugin="null")[0]["result"]


for tasklet_path in test_paths:
    task_path = os.path.dirname(tasklet_path)
    if task_path not in tests:
        tests.append(task_path)
failed = 0


for test in tests:
    print(f"running test {test}:")
    try:
        for retval in task.run(test, cfg, output_plugin="null"):
            tasklet_path = retval["tasklet_path"]
            tasklet_return_value = retval["result"]
            tasklet_error = retval["error"]
            tasklet_status = retval["status"]
            tasklet_skipped = retval["skipped"]
            print(f"\t{os.path.basename(tasklet_path)}", end=" ")
            if (
                "/content/" in tasklet_path
                or "/api/" in tasklet_path
                or "/tasks/" in tasklet_path
            ):
                if tasklet_return_value == "OK":
                    print(Fore.GREEN + str(tasklet_return_value))
                else:
                    print(Fore.RED + str(tasklet_error).split("\n")[0])
                    print(Style.RESET_ALL, end="")
                    failed += 1
                    for skipped_task in tasklet_skipped:
                        print("\t" + skipped_task + Fore.YELLOW + " SKIPPED")

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
print(f"Logfile for this run is {log_file}")
if failed:
    sys.exit(1)
