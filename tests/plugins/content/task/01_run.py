ok = True
for retval in task.run(".subtask1/", output_plugin="null"):
    if "01_tasklet_1" not in retval["tasklet_path"]:
        ok = False
    if retval["result"] != "OK":
        ok = False

if ok:
    return "OK"
else:
    return "NOT OK"
