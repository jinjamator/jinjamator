retval=""

# load excel from path defined in defaults.yaml (excel_data_path) and iterate over each line
for line_no,cfg in file.excel.load(excel_data_path).items():
    # run subtask/subtasklet without an output plugin and inject excel data into self.configuration of the subtask
    if cfg.get("remove"):
        cfg["undo"]=True
    result=task.run(".subtasks/create_vlan_ios",{**self.configuration,**cfg}, output_plugin="null")[0] 
    # as we have just a single tasklet so the result is always in [0]

    if result["status"] == "ok":
        retval += "\n" + result["result"]
    else:
        log.error(result["error"])

return retval