vmware.vsphere.vm
===============================================

.. toctree::
    :maxdepth: 1

    vmware.vsphere.vm.nics.rst


.. py:function:: vmware.vsphere.vm.get(attr_name, attr_value, obj, **kwargs):

    Get a specific VM identified by an attribute. Will only return the first object that matches

    :param attr_name: Name of the attribute that shall be used for selecting the object. Can also be "rel_path" to match a specific path within a folder-structure. Be aware, that this will trigger a 'get_dict' which may take a while.
    :type obj: string
    :param attr_value: Value which attr_name must contain
    :type obj: string
    :param obj: The object within we shall search for the host
    :type obj: object
    :return: First object that matched the selection. Returns bool:False if no match was found
    :rtype: object

    :Keyword Arguments:
        * *vc_obj* (``object``)
          vCenter-object that was created by vmware.vsphere.get_content(). This will overwrite the object that was registered as default by vmware.vsphere.default()
    

.. py:function:: vmware.vsphere.vm.get_cluster(obj):

    Get the cluster which hosts the VM

    :param obj: The VM-object
    :type obj: object
    :return: List of objects
    :rtype: list
    

.. py:function:: vmware.vsphere.vm.get_datastore_clusters(obj):

    Get a list of all datastore-clusters that are used by the VM

    :param obj: The VM-object
    :type obj: object
    :return: List of objects
    :rtype: list
    

.. py:function:: vmware.vsphere.vm.get_datastores(obj):

    Get a list of all datastores that are used by the VM

    :param obj: The VM-object
    :type obj: object
    :return: List of objects
    :rtype: list
    

.. py:function:: vmware.vsphere.vm.get_dict(obj, **kwargs):

    Get all VMs beneath the object and return a dictionary.

    :param obj: The object within we shall search for VMs (datacenter; cluster is not yet implemented)
    :type obj: object
    :return: Dictionary containing a key -> value pair per VM
    :rtype: dict

    :Keyword Arguments:
        * *key* (``string``)
          String containing the attribute-name that shall be used as the dictionary-key. May be "rel_path" to construct a relative path, which is descriptive and unique containing all the folders (default). Make sure to choose a unique attribute, otherwise elements will overwrite each other.
        * *key_prepend* (``string``)
          String which should be prepended to all keys that are built within this function
    

.. py:function:: vmware.vsphere.vm.get_folder(obj):

    Get the parent folder in which the VM is situated

    :param obj: The VM-object
    :type obj: object
    :return: List of objects
    :rtype: list
    

.. py:function:: vmware.vsphere.vm.get_host(obj):

    Get the host which hosts the VM

    :param obj: The VM-object
    :type obj: object
    :return: List of objects
    :rtype: list
    

.. py:function:: vmware.vsphere.vm.get_list(obj, **kwargs):

    Get all VMs beneath the object and return a list.
    This function is much faster than get_dict() when the vCenter-object is present (passed within *kwargs* or present as default)

    :param obj: The object within we shall search for VMs
    :type obj: object
    :return: List of objects
    :rtype: list

    :Keyword Arguments:
        * *vc_obj* (``object``)
          vCenter-object that was created by vmware.vsphere.get_content(). This will overwrite the object that was registered as default by vmware.vsphere.default()
    

.. py:function:: vmware.vsphere.vm.get_networks(obj):

    Get a list of all networks (portgroups) that are used by the VM

    :param obj: The VM-object
    :type obj: object
    :return: List of objects
    :rtype: list
    

.. py:function:: vmware.vsphere.vm.get_respool(obj):

    Get the respool in which the VM resides

    :param obj: The VM-object
    :type obj: object
    :return: List of objects
    :rtype: list
    

.. py:function:: vmware.vsphere.vm.is_type(obj):

    Check if passed object is a VM

    :param obj: The object
    :type obj: object
    :return: True if it is a VM, false if not
    :rtype: bool
    

.. py:function:: vmware.vsphere.vm.is_vm(obj):

    Check if passed object is a VM

    :param obj: The object
    :type obj: object
    :return: True if it is a VM, false if not
    :rtype: bool
    


