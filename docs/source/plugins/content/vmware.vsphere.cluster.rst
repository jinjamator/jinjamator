vmware.vsphere.cluster
===============================================

.. toctree::
    :maxdepth: 1

    vmware.vsphere.cluster.respool.rst


.. py:function:: vmware.vsphere.cluster.get(attr_name, attr_value, obj, **kwargs):

    Get a specific cluster identified by an attribute. Will only return the first object that matches

    :param attr_name: Name of the attribute that shall be used for selecting the object. Can also be "rel_path" to match a specific path within a folder-structure. Be aware, that this will trigger a 'get_dict' which may take a while.
    :type obj: string
    :param attr_value: Value which attr_name must contain
    :type obj: string
    :param obj: The object within we shall search for clusters (datacenter or folder)
    :type obj: object
    :return: First object that matched the selection. Returns bool:False if no match was found
    :rtype: object

    :Keyword Arguments:
        * *vc_obj* (``object``)
          vCenter-object that was created by vmware.vsphere.get_content(). This will overwrite the object that was registered as default by vmware.vsphere.default()
    

.. py:function:: vmware.vsphere.cluster.get_datastore_clusters(obj):

    Get a list of all datastore-clusters in the cluster

    :param obj: The cluster-object
    :type obj: object
    :return: List of objects
    :rtype: list
    

.. py:function:: vmware.vsphere.cluster.get_datastores(obj):

    Get a list of all datastores in the cluster

    :param obj: The cluster-object
    :type obj: object
    :return: List of objects
    :rtype: list
    

.. py:function:: vmware.vsphere.cluster.get_dict(obj, **kwargs):

    Get all clusters beneath the object and return a dictionary. If neighter "cluster" or "standalone" are explicitly set to True, both are fetched

    :param obj: The object within we shall search for clusters (datacenter or folder)
    :type obj: object
    :return: Dictionary containing a key -> value pair per cluster
    :rtype: dict

    :Keyword Arguments:
        * *key* (``string``)
          String containing the attribute-name that shall be used as the dictionary-key. May be "rel_path" to construct a relative path, which is descriptive and unique containing all the folders (default). Make sure to choose a unique attribute, otherwise elements will overwrite each other.
        * *cluster* (``bool``)
          Get clusters
        * *standalone* (``bool``)
          Get standalone hosts ("single clusters")
    

.. py:function:: vmware.vsphere.cluster.get_hosts(obj):

    Get a list of all hosts in the cluster

    :param obj: The cluster-object
    :type obj: object
    :return: List of objects
    :rtype: list
    

.. py:function:: vmware.vsphere.cluster.get_list(obj, **kwargs):

    Get all clusters beneath the object and return a list. If neighter "cluster" or "standalone" are explicitly set to True, both are fetched.
    This function is much faster than get_dict() when the vCenter-object is present (passed within *kwargs* or present as default)

    :param obj: The object within we shall search for clusters (datacenter or folder)
    :type obj: object
    :return: List of objects
    :rtype: list

    :Keyword Arguments:
        * *cluster* (``bool``)
          Get clusters
        * *standalone* (``bool``)
          Get standalone hosts ("single clusters")
        * *vc_obj* (``object``)
          vCenter-object that was created by vmware.vsphere.get_content(). This will overwrite the object that was registered as default by vmware.vsphere.default()
    

.. py:function:: vmware.vsphere.cluster.get_respools(obj):

    Get a list of all resource-pools in the cluster

    :param obj: The cluster-object
    :type obj: object
    :return: List of objects
    :rtype: list
    

.. py:function:: vmware.vsphere.cluster.is_cluster(obj):

    Check if passed object is a cluster

    :param obj: The object
    :type obj: object
    :return: True if it is a cluster, false if not
    :rtype: bool
    

.. py:function:: vmware.vsphere.cluster.is_type(obj):

    Check if passed object is a cluster

    :param obj: The object
    :type obj: object
    :return: True if it is a cluster, false if not
    :rtype: bool
    


