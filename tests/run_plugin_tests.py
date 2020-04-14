#!/usr/bin/env -S jinjamator -t
from glob import glob
import os
from colorama import init

init()
from colorama import Fore, Style

tests = []


apic_url, apic_username, apic_password, ssh_host, ssh_username, ssh_password

for tasklet_path in glob(
    f"{os.path.dirname(__file__)}{os.path.sep}plugins/{os.path.sep}**{os.path.sep}*.*", recursive=True):
    task_path = os.path.dirname(tasklet_path)
    if task_path not in tests:
        tests.append(task_path)

for test in tests:
    print(f"running test {test}:")
    for tasklet_path, tasklet_return_value in task.run(
        test, output_plugin="null"
    ).items():
        print(f"\t{os.path.basename(tasklet_path)}", end=" ")
        if tasklet_return_value == "OK":
            print(Fore.GREEN + tasklet_return_value)
        else:
            print(Fore.RED + tasklet_return_value)
        print(Style.RESET_ALL, end="")
