ok = True
for subtask_path, return_value in task.run("subtask1/", output_plugin="null").items():
    if "01_tasklet_1" not in subtask_path:
        ok = False
    if return_value != "OK":
        ok = False

if ok:
    return "OK"
else:
    return "NOT OK"
