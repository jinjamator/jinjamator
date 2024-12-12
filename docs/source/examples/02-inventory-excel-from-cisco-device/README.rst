
Create An Inventory Excel From A Cisco IOS Device
---------------------------------------------------


**Simple implementation for a single host:**

The task code, written in Python, consists of a single line. Since the task code is encapsulated within a function, it can and should return data, which will then be passed to the output plugin.

.. literalinclude:: 01_super_simple_ios/run.py
  :language: python


All default values for the task can be defined in the defaults.yaml file and overridden using -m <key>:<value>.

.. literalinclude:: 01_super_simple_ios/defaults.yaml
  :language: yaml


**More advanced implementation for multiple hosts:**


.. literalinclude:: 02_inventory_for_multiple_hosts/run.py
  :language: python

.. literalinclude:: 02_inventory_for_multiple_hosts/defaults.yaml
  :language: yaml


**More advanced implementation for multiple hosts with enhanced GUI:**

.. literalinclude:: 03_inventory_for_multiple_hosts_enhanced_gui/run.py
  :language: python

.. literalinclude:: 03_inventory_for_multiple_hosts_enhanced_gui/defaults.yaml
  :language: yaml

.. literalinclude:: 03_inventory_for_multiple_hosts_enhanced_gui/schema.yaml
  :language: yaml
