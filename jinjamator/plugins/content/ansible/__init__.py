# Experimental implementation to run ansible playbooks
import logging


try:
    import ansible_runner
except ModuleNotFoundError:
    logging.debug("module ansible_runner not installed")


def run(playbook, inv, **kwargs):
    log.console(f"Running {playbook} for {inv}")

    play_path = ""
    if "\n" not in playbook:
        # there is no newline in the playbook
        if len(playbook) < 512:
            # playbook is shorter than 512 chars (single line playbook somehow)
            if file.exists(playbook):
                if file.get_suffix(playbook) == "j2":
                    # File is a jinja-file, we are supposed to feed it to the jinja2 engine first
                    if "data" in kwargs.keys():
                        data = kwargs["data"]
                    else:
                        data = {}

                    # log.console(f"J2 rendering. passed data is: {json.dumps(data)}")
                    if isinstance(_jinjamator, object):
                        task_data = {**_jinjamator.configuration, **data}
                    else:
                        task_data = data
                    # task_data = data
                    # log.console(f"data after merge: {json.dumps(task_data)}")
                    # if _jinjamator: print(f"_jinjamator does exist: {type(_jinjamator)}")
                    # if _jinjamator.configuration: print(f"_jinjamator.configuration does exist: {type(_jinjamator.configuration)}")
                    # if _jinjamator.configuration._data: print(f"_jinjamator.configuration._data does exist: {type(_jinjamator.configuration._data)}")

                    # Get rendered data and store it - it will be written and executed later
                    # Untested because calling task.run() j2 from content-plugin does currently not work
                    playbook = task.run(playbook, task_data=task_data)[0]["result"]
                    play_path = ""  # to be sure
                else:
                    # Just an ordinary playbook
                    play_path = playbook
            else:
                log.error(f"Cannot find playbook: {playbook}")
                play_path = False

    if isinstance(play_path, str) and play_path == "":
        # playbook might be a string for all we can tell
        # create a tmpfile, save it there and feed it into ansible
        play_path = file.temp.file().name
        file.save(playbook, play_path)

    return ansible_runner.run(playbook=play_path, inventory=inv)


def simple_inventory(hosts):
    # Create a simple inventory that can be passed to run()
    inv = {"all": {"hosts": {}}}

    for h in hosts:
        inv["all"]["hosts"][h] = {}

    return inv

def reverse_order (playbook):
    #Reverse the order of jobs and tasks
    #used in combination with undo = True
    #parse the yaml
    pby = yaml.loads(playbook)
    #Reverse jobs
    pby.reverse()

    #Reverse tasks in each job
    for jobs in pby:
        jobs['tasks'].reverse()
    
    return yaml.dumps(pby)
