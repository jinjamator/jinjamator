ssh
===============================================

.. toctree::
    :maxdepth: 1



.. py:function:: ssh.configure(commands_or_path, connection=None, _requires=<function _get_missing_ssh_connection_vars at 0x7f9dcc7d6700>, **kwargs):

    not documented yet

.. py:function:: ssh.connect(_requires=<function _get_missing_ssh_connection_vars at 0x7f9dcc7d6700>, **kwargs):

    Run a command via SSH and return the text output.

    :param command: The command that should be run.
    :type command: ``str``
    :raises Exception: If the command cannot be run on the remote device and best_effort is not set within the task.
    :return: The text output of the command.
    :rtype: ``str``

    :Keyword Arguments:
        * *ssh_username* (``str``), ``optional``, ``jinjamator enforced`` --
           Username for the SSH connection. If not set in task configuration or via keyword argument jinjamator asks the user to input the data.
        * *ssh_password* (``str``), ``optional``, ``jinjamator enforced`` --
           Password for the SSH connection. If not set in task configuration or via keyword argument jinjamator asks the user to input the data.
        * *ssh_host*  (``str``), ``optional``, ``jinjamator enforced`` --
           Target hostname or IP address for the SSH connection. If not set in task configuration or via keyword argument jinjamator asks the user to input the data.
        * *ssh_port* (``int``), ``optional`` --
           SSH TCP port, defaults to 22
        * *ssh_device_type* (``str``), ``optional`` --
           Netmiko device type, defaults to "cisco_nxos". 
           Currently supported device_types can be found here: https://github.com/ktbyers/netmiko/tree/develop/netmiko 
        * *fast_cli* (``bool``), ``optional`` --
           Use Netmiko fast_cli mode, defaults to False
        * *verbose* (``bool``), ``optional`` --
           Set Netmiko to debug mode, defaults to False

    :Examples:
        If one of the following conditions are met,
            * *ssh_username*, *ssh_password*, *ssh_host* is specified via command line parameter in CLI Mode e.g -m 'ssh_username':'admin'
            * Any of *ssh_username*, *ssh_password*, *ssh_host* is not specified via command line parameter in CLI Mode and the user enters the data correctly via CLI.
            * The task is run via Daemon mode and ssh_username, ssh_password, ssh_host are defined in the task defaults.yaml, environment site defaults.yaml.
            * The task is run via Daemon mode and ssh_username, ssh_password, ssh_host are entered correctly in the generated webform.
            
        
        the raw output of the command show inventory from a cisco nxos box is returned by the tasklet .

        jinja2 tasklet:
        
            .. code-block:: jinja
                
                {{ssh.run('show inventory')}} 

        python tasklet:

            .. code-block:: python

                return ssh.run('show inventory')

        To set the arguments directly on call of the function. The example will ask for the password and connects to 1.2.3.4 port 22 and runs the command "show inventory"

        jinja2 tasklet:
        
            .. code-block:: jinja
                
                {{ssh.run('show inventory',ssh_username=admin,ssh_host='1.2.3.4')}} 

        python tasklet:

            .. code-block:: python

                return ssh.run('show inventory',ssh_username='admin','ssh_host'='1.2.3.4')


    

.. py:function:: ssh.disconnect(connection):

    not documented yet

.. py:function:: ssh.get_file(src, dst, connection=None, _requires=<function _get_missing_ssh_connection_vars at 0x7f9dcc7d6700>, **kwargs):

    not documented yet

.. py:function:: ssh.put_file(src, dst, connection=None, _requires=<function _get_missing_ssh_connection_vars at 0x7f9dcc7d6700>, **kwargs):

    not documented yet

.. py:function:: ssh.query(command, connection=None, _requires=<function _get_missing_ssh_connection_vars at 0x7f9dcc7d6700>, **kwargs):

    not documented yet

.. py:function:: ssh.run(command, connection=None, _requires=<function _get_missing_ssh_connection_vars at 0x7f9dcc7d6700>, **kwargs):

    not documented yet

.. py:function:: ssh.run_mlt(commands, connection=None, _requires=<function _get_missing_ssh_connection_vars at 0x7f9dcc7d6700>, **kwargs):

    not documented yet


