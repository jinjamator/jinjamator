ansible
===============================================

.. toctree::
    :maxdepth: 1



.. py:function:: ansible.reverse_order(playbook):

    Reverses the tasks within a playbook.
    Actually useful when using undo

    Args:
        playbook (str): string containing the playbook (not a filename)

    Returns:
        str: The reversed playbook string
    

.. py:function:: ansible.run(playbook, inv, **kwargs):

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
    

.. py:function:: ansible.simple_inventory(hosts):

    Creates a simple ansible compatible inventory dictionary of the given hist-list

    Args:
        hosts (list): List of hosts that should be part of the inventory

    Returns:
        dict: Very simple ansible inventory
    


