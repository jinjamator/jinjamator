
Create Some Configuration using Excel and Subtasks
---------------------------------------------------

This task uses an excel file as input to generate some cisco ios configuration using subtasks.

.. xlsx-table:: Demo Excel Data (data.xlsx)
   :file: data.xlsx
   :header-rows: 1

The task just loads the excel data, calls the subtask subtasks/create_vlan_ios/create_vlan.ios.j2 and returns the collected results

.. literalinclude:: run.py
  :language: python
  :caption: run.py

In the main task defaults just the path to the excel data is configured

.. literalinclude:: defaults.yaml
  :language: yaml
  :caption: defaults.yaml

The subtask is written as jinja2 task and has it's own defaults.yaml

.. literalinclude:: .subtasks/create_vlan_ios/create_vlan.ios.j2
  :language: jinja
  :caption: .subtasks/create_vlan_ios/create_vlan.ios.j2


.. literalinclude:: .subtasks/create_vlan_ios/defaults.yaml
  :language: yaml
  :caption: .subtasks/create_vlan_ios/defaults.yaml

The result of this task is a valid cisco ios vlan configuration.

.. literalinclude:: result.ios
  :language: cisco
  :caption: result.ios

.. .. literalinclude:: schema.yaml
..   :language: yaml
