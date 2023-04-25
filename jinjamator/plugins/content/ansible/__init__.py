# Experimental implementation to run ansible playbooks

import logging

#Do not fail when there is no ansible_runner present on systems that do not use it
#As the plugin is experimental ansible_runner might not be a hard dependency

try:
    import ansible_runner
except ModuleNotFoundError:
    logging.debug("module ansible_runner not installed")


def run(playbook, inv, **kwargs):
    """
    Runs the given playbook on inventory.
    Playbook may be the whole playbook, a filepath or a j2 file that shall be rendered

    Args:
        playbook (string): The playbook as string OR the filename of the playbook OR the filename of a j2 template that shall be rendered
        inv (dict): A dict containing the inventory where the playbook shall be run
    
    Keyword Args:
        undo (boolean): Run the playbook as "undo" if it supports it. Will set the undo-flag and reverse the order. Will only work with proper written j2 templates and will overwrite the 'undo' key in the data dict
        data (dict): Dictionary containing the variables that shall be passed to the j2 template

    Returns:
        object(ansible_runner.runner.Runner): The return of ansible_runner.run()
    """

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

                    #Set undo in data if the undo keyword is set
                    if 'undo' in kwargs:
                        data['undo'] = kwargs['undo']
                    
                    # log.console(f"J2 rendering. passed data is: {json.dumps(data)}")
                    #merge jinjamator config with data - if jinjamator.configuration is an object
                    if isinstance(_jinjamator, object):
                        task_data = {**_jinjamator.configuration, **data}
                    else:
                        task_data = data

                    # Get rendered data and store it - it will be written and executed later
                    playbook = task.run(playbook, task_data=task_data)[0]["result"]
                    play_path = ""  # to be sure

                    #Also, do the undo-handling here if the parameter was set
                    if 'undo' in data and data['undo'] == True:
                        playbook = reverse_order(playbook)
                        
                else:
                    # Just an ordinary playbook
                    play_path = playbook
                    #play_path = ""
                    #Always read the playbook so we can do modifications
                    #playbook = file.load(playbook)
            else:
                #In this case the playbook is very short but not a file
                #We will try to run int regardless
                #log.error(f"Cannot find playbook: {playbook}")
                play_path = ''

    if isinstance(play_path, str) and play_path == "":
        # playbook might be a string for all we can tell
        # create a tmpfile, save it there and feed it into ansible
        play_path = file.temp.file().name
        file.save(playbook, play_path)

    return ansible_runner.run(playbook=play_path, inventory=inv)


def simple_inventory(hosts):
    """
    Creates a simple ansible compatible inventory dictionary of the given hist-list

    Args:
        hosts (list): List of hosts that should be part of the inventory

    Returns:
        dict: Very simple ansible inventory
    """
    # Create a simple inventory that can be passed to run()
    inv = {"all": {"hosts": {}}}

    for h in hosts:
        inv["all"]["hosts"][h] = {}

    return inv

def reverse_order (playbook):
    """
    Reverses the tasks within a playbook.
    Actually useful when using undo

    Args:
        playbook (str): string containing the playbook (not a filename)

    Returns:
        str: The reversed playbook string
    """
    #Reverse the order of jobs and tasks
    #parse the yaml
    pby = yaml.loads(playbook)
    #Reverse jobs
    pby.reverse()

    #Reverse tasks in each job
    for jobs in pby:
        jobs['tasks'].reverse()
    
    return yaml.dumps(pby)
