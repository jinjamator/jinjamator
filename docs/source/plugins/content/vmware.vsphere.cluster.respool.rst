vmware.vsphere.cluster.respool
===============================================

.. toctree::
    :maxdepth: 1



.. py:function:: vmware.vsphere.cluster.respool.get(attr_name, attr_value, obj, **kwargs):

    Get a specific resource-pools identified by an attribute. Will only return the first object that matches

    :param attr_name: Name of the attribute that shall be used for selecting the object. Can also be "rel_path" to match a specific path within a folder-structure. Be aware, that this will trigger a 'get_dict' which may take a while.
    :type obj: string
    :param attr_value: Value which attr_name must contain
    :type obj: string
    :param obj: The object within we shall search for resource-pools (cluster)
    :type obj: object
    :return: First object that matched the selection. Returns bool:False if no match was found
    :rtype: object

    :Keyword Arguments:
        * *vc_obj* (``object``)
          vCenter-object that was created by vmware.vsphere.get_content(). This will overwrite the object that was registered as default by vmware.vsphere.default()
    

.. py:function:: vmware.vsphere.cluster.respool.get_dict(obj, **kwargs):

    Get all resource-pools beneath the object and return a dictionary.

    :param obj: The object within we shall search for resource-pools (cluster)
    :type obj: object
    :return: Dictionary containing a key -> value pair per respool
    :rtype: dict

    :Keyword Arguments:
        * *key* (``string``)
          String containing the attribute-name that shall be used as the dictionary-key. May be "rel_path" to construct a relative path, which is descriptive and unique containing all the folders (default). Make sure to choose a unique attribute, otherwise elements will overwrite each other.
    

.. py:function:: vmware.vsphere.cluster.respool.get_list(obj, **kwargs):

    Get all resource-pools beneath the object and return a list.
    This function is much faster than get_dict() when the vCenter-object is present (passed within *kwargs* or present as default)

    :param obj: The object within we shall search for resource-pools (cluster)
    :type obj: object
    :return: List of objects
    :rtype: list

    :Keyword Arguments:
        * *vc_obj* (``object``)
          vCenter-object that was created by vmware.vsphere.get_content(). This will overwrite the object that was registered as default by vmware.vsphere.default()
    

.. py:function:: vmware.vsphere.cluster.respool.is_respool(obj):

    Check if passed object is a resource-pool

    :param obj: The object
    :type obj: object
    :return: True if it is a resource-pool, false if not
    :rtype: bool
    

.. py:function:: vmware.vsphere.cluster.respool.is_type(obj):

    Check if passed object is a resource-pool

    :param obj: The object
    :type obj: object
    :return: True if it is a resource-pool, false if not
    :rtype: bool
    


