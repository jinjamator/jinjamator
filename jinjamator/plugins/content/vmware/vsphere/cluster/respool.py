from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim

def get_dict (obj,**kwargs):
    """
    Get all resource-pools beneath the object and return a dictionary.

    :param obj: The object within we shall search for resource-pools (cluster)
    :type obj: object
    :return: Dictionary containing a key -> value pair per respool
    :rtype: dict

    :Keyword Arguments:
        * *key* (``string``)
          String containing the attribute-name that shall be used as the dictionary-key. May be "rel_path" to construct a relative path, which is descriptive and unique containing all the folders (default). Make sure to choose a unique attribute, otherwise elements will overwrite each other.
    """
    if 'key' in kwargs and kwargs['key']: key = kwargs['key']
    else: key = "rel_path"

    #Go into root-folder if object has one
    if hasattr(obj,'resourcePool'):
        return vmware.vsphere.recurse_objects_dict(obj,"resourcePool",key=key)   
    else:
        log.info(f"Could not find expected attribute 'resourcePool' in {obj}")
        return dict()


def get_list (obj,**kwargs):
    """
    Get all resource-pools beneath the object and return a list. 
    This function is much faster than get_dict() when the vCenter-object is present (passed within *kwargs* or present as default)

    :param obj: The object within we shall search for resource-pools (cluster)
    :type obj: object
    :return: List of objects
    :rtype: list

    :Keyword Arguments:
        * *vc_obj* (``object``)
          vCenter-object that was created by vmware.vsphere.get_content(). This will overwrite the object that was registered as default by vmware.vsphere.default()
    """
    vc = vmware.vsphere.get_vc_obj(kwargs)
    
    if hasattr(obj,'resourcePool'):
        if vc: ret = vmware.vsphere.view.container(vc,obj,vim.ResourcePool,recurse=True)
        else:
            ret = []
            for k,v in get_dict(obj).items():
                ret.append(v)
        
        return ret

    else:
        log.info(f"Could not find expected attribute 'resourcePool' in {obj}")
        return list()


def get (attr_name,attr_value,obj,**kwargs):
    """
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
    """
    #Rewrite id to _moId
    if attr_name == 'id': attr_name = "_moId"
    vc = vmware.vsphere.get_vc_obj(kwargs)

    log.debug(f"Getting respool where {attr_name} is {attr_value}")

    if attr_name == 'rel_path':
        objects = get_dict(obj,key='rel_path')
        if objects:
            for k,o in objects.items():
                if k == attr_value:
                    return o
    else:
        objects = get_list(obj,vc_obj=vc)
        
        for o in objects:
            if hasattr(o,attr_name):
                if getattr(o,attr_name) == attr_value:
                    return o
    
    return False


def is_respool (obj):
    """
    Check if passed object is a resource-pool

    :param obj: The object
    :type obj: object
    :return: True if it is a resource-pool, false if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.ResourcePool')


def is_type (obj):
    """
    Check if passed object is a resource-pool

    :param obj: The object
    :type obj: object
    :return: True if it is a resource-pool, false if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.ResourcePool')