vmware.vsphere
===============================================

.. toctree::
    :maxdepth: 1

    vmware.vsphere.cluster.rst
    vmware.vsphere.datacenter.rst
    vmware.vsphere.datastore.rst
    vmware.vsphere.folder.rst
    vmware.vsphere.host.rst
    vmware.vsphere.hosts.rst
    vmware.vsphere.view.rst
    vmware.vsphere.vm.rst
    vmware.vsphere.vms.rst
    vmware.vsphere.vswitch.rst


.. py:function:: vmware.vsphere.connect(host=None, username=None, password=None, cache=True):

    Connect to vCenter

    :param host: Hostname or IP-address
    :type host: string
    :param username: Username
    :type username: string
    :param password: Passwords
    :type password: string
    :param cache: Write object to cache if set to True
    :type cache: bool
    :return: Service-instance object
    :rtype: object
    

.. py:function:: vmware.vsphere.default(obj):

    Set the object as default vCenter-object (highly recommended)

    :param obj: The object
    :type obj: object
    :return: Returns the object again
    :rtype: object
    

.. py:function:: vmware.vsphere.error_no_vc(**kwargs):

    Generates an error (function for lazy men)

    :return: nothing
    :rtype: none
    

.. py:function:: vmware.vsphere.get_absolute_path(obj):

    Gets the absolute path from the given object as long as there is a parent

    :param obj: The object
    :type obj: object
    :return: String of all parents seperated by /
    :rtype: string
    

.. py:function:: vmware.vsphere.get_content(service_instance=None, cache=True):

    Get the content of the service_instance
    It is highly recommended to use vmware.vsphere.default() on the return value

    :param service_instance: The service_instance created by connect()
    :type service_instance: object
    :param cache: Write object to cache if set to True
    :type cache: bool
    :return: Content object
    :rtype: object
    

.. py:function:: vmware.vsphere.get_first_parent_type(attr, parent_type):

    Gets the first parent of an attribute that matches the given type

    :param obj: The attribute-object
    :type obj: object
    :param obj: The type of the object
    :type obj: string
    :return: First parent-object that matches the type
    :rtype: object
    

.. py:function:: vmware.vsphere.get_id(obj):

    Get the ID (_moId) of the object

    :param obj: The object
    :type obj: object
    :return: The ID-string (_moId). Empty string if there is no ID
    :rtype: string
    

.. py:function:: vmware.vsphere.get_obj(vimtype, name, content=None):

    not documented yet

.. py:function:: vmware.vsphere.get_objects_dict(obj, obj_type='*', **kwargs):

    Get all objects within an an object-attribute and return them as dict
    Can filter by object-type if specified

    :param obj: The object-attribute containing a list of entries
    :type obj: list
    :param obj_type: Object-type that should be returned. Default is "*" to disable filtering
    :type obj_type: string
    :return: Dict of matching items
    :rtype: dict

    :Keyword Arguments:
        * *key* (``string``)
          The name of the attribute that should be used as dict-key.
    

.. py:function:: vmware.vsphere.get_objects_list(obj, obj_type='*'):

    Get all objects within an an object-attribute and return them as list
    Can filter by object-type if specified

    :param obj: The object-attribute containing a list of entries
    :type obj: list
    :param obj_type: Object-type that should be returned. Default is "*" to disable filtering
    :type obj_type: string
    :return: List of matching items
    :rtype: list
    

.. py:function:: vmware.vsphere.get_vc_obj(kwargs):

    Gets the vc_object from passed kwargs or the default set by vmware.vsphere.default()

    :param kwargs: kwargs passed into the parent function
    :type kwargs: dict
    :return: vCenter-object or False
    :rtype: object
    

.. py:function:: vmware.vsphere.has_parent(obj):

    Checks if the object has a parent

    :param obj: The object
    :type obj: object
    :return: True or False
    :rtype: bool
    

.. py:function:: vmware.vsphere.is_obj_type(obj, type_name):

    Check if passed object is matching the passed type. This is currently not a strict match as "type_name" is a string and needs only to be a subset of str(type(obj))

    :param obj: The object
    :type obj: object
    :param type_name: The type
    :type type_name: string
    :return: True or False
    :rtype: bool
    

.. py:function:: vmware.vsphere.is_type(obj):

    Check if passed object is a vCenter

    :param obj: The object
    :type obj: object
    :return: True if it is a vCenter, False if not
    :rtype: bool
    

.. py:function:: vmware.vsphere.is_vc(obj):

    Check if passed object is a vCenter

    :param obj: The object
    :type obj: object
    :return: True if it is a vCenter, False if not
    :rtype: bool
    

.. py:function:: vmware.vsphere.list_make_unique(elements):

    Removes duplicates from a list of elements

    :param elements: List of elements
    :type elements: list
    :return: deduplicated list
    :rtype: list
    

.. py:function:: vmware.vsphere.parent_is_type(obj, parent_type):

    Checks if the parent matches the given type

    :param obj: The object
    :type obj: object
    :param parent_type: The expected type of the parent
    :type parent_type: string
    :return: True or False
    :rtype: bool
    

.. py:function:: vmware.vsphere.recurse_child(obj, childType, key=False):

    Recurse all child-objects (childEntity) and feed them into a dict or list. Recurse until no child is left.
    Childs will also be filtered by childType
    If a key is passed, a dict will be created. Otherwise it will be a list

    :param obj: The object containing the childs
    :type obj: object
    :param childType: Child-type that should be fetched
    :type childType: string
    :param key: The name of the attribute that should be used as dict-key. May be "rel_path" to construct a unique path. Ommit to get a list
    :type key: string
    :return: Dict or list of matching items
    :rtype: dict or list

    

.. py:function:: vmware.vsphere.recurse_child_dict(obj, childType, key, **kwargs):

    Recurse all child-objects (childEntity) and feed them into a dict. Recurse until no child is left.
    Childs will also be filtered by childType

    :param obj: The object containing the childs
    :type obj: object
    :param childType: Child-type that should be fetched
    :type childType: string
    :param key: The name of the attribute that should be used as dict-key. May be "rel_path" to construct a unique path
    :type key: string
    :return: Dict of matching items
    :rtype: dict

    :Keyword Arguments:
        * *key_prepend* (``string``)
          String which should be prepended to all keys that are built within this function
    

.. py:function:: vmware.vsphere.recurse_child_list(obj, childType, **kwargs):

    Recurse all child-objects (childEntity) and feed them into a list. Recurse until no child is left.
    Childs will also be filtered by childType

    :param obj: The object containing the childs
    :type obj: object
    :param childType: Child-type that should be fetched
    :type childType: string
    :return: List of matching items
    :rtype: list

    :Keyword Arguments:
        Currently none
    

.. py:function:: vmware.vsphere.recurse_objects_dict(obj, attr_name, **kwargs):

    Recurse through all objects that are contained in the given attribute (attr_name).

    :param obj: The object
    :type obj: object
    :param attr_name: The name of the attribute that shall be recursed
    :type attr_name: string
    :return: Dict of matching items
    :rtype: dict

    :Keyword Arguments:
        * *key* (``string``)
          The name of the attribute that should be used as dict-key.
        * *key_prepend* (``string``)
          String which should be prepended to all keys that are built within this function
    

.. py:function:: vmware.vsphere.recurse_objects_list(obj, attr_name, **kwargs):

    Recurse through all objects that are contained in the given attribute (attr_name).

    :param obj: The object
    :type obj: object
    :param attr_name: The name of the attribute that shall be recursed
    :type attr_name: string
    :return: List of matching items
    :rtype: list

    :Keyword Arguments:
        Currently none
    

.. py:function:: vmware.vsphere.recurse_parent_if_type_not(obj, parent_type):

    Recurse through parents of the object until the parent type is the given type or no parent is left

    :param obj: The object
    :type obj: object
    :param obj: The type of the parent object to look out for
    :type obj: string
    :return: First parent-object that matches the type
    :rtype: object
    


