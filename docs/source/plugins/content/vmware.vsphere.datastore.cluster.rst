vmware.vsphere.datastore.cluster
===============================================

.. toctree::
    :maxdepth: 1



.. py:function:: vmware.vsphere.datastore.cluster.get(attr_name, attr_value, obj, **kwargs):

    Get a specific datastore-clusters identified by an attribute. Will only return the first object that matches

    :param attr_name: Name of the attribute that shall be used for selecting the object. Using "rel_path" will fail and generate an error
    :type obj: string
    :param attr_value: Value which attr_name must contain
    :type obj: string
    :param obj: The object within we shall search for the datastore-cluster
    :type obj: object
    :return: First object that matched the selection. Returns bool:False if no match was found
    :rtype: object

    :Keyword Arguments:
        * *vc_obj* (``object``)
          vCenter-object that was created by vmware.vsphere.get_content(). This will overwrite the object that was registered as default by vmware.vsphere.default()
    

.. py:function:: vmware.vsphere.datastore.cluster.get_datastores(obj, **kwargs):

    Get a list of all datastore within the datastore-cluster

    :param obj: The datastore-cluster-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    

.. py:function:: vmware.vsphere.datastore.cluster.get_dict(obj, **kwargs):

    This function is not yet implemented
    

.. py:function:: vmware.vsphere.datastore.cluster.get_list(obj, **kwargs):

    Get all datastore-clusters beneath the object and return a list.
    This function **requires** the vCenter-object to be present (passed within *kwargs* or present as default)

    :param obj: The object within we shall search for datastore-clusters
    :type obj: object
    :return: List of objects
    :rtype: list

    :Keyword Arguments:
        * *vc_obj* (``object``)
          vCenter-object that was created by vmware.vsphere.get_content(). This will overwrite the object that was registered as default by vmware.vsphere.default()
    

.. py:function:: vmware.vsphere.datastore.cluster.get_vms(obj, **kwargs):

    Get a list of all VMs using the datastore-cluster

    :param obj: The datastore-cluster-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    

.. py:function:: vmware.vsphere.datastore.cluster.is_datastore_cluster(obj):

    Check if passed object is a datastore-cluster

    :param obj: The object
    :type obj: object
    :return: True if it is a datastore-cluster, false if not 
    :rtype: bool
    

.. py:function:: vmware.vsphere.datastore.cluster.is_type(obj):

    Check if passed object is a datastore-cluster

    :param obj: The object
    :type obj: object
    :return: True if it is a datastore-cluster, false if not 
    :rtype: bool
    


