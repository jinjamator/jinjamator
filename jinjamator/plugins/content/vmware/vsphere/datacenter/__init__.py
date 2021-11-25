from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim

def get_dict (obj,**kwargs):
    """
    Get all datacenters beneath the object and return a dictionary. 

    :param obj: The object within we shall search for datacenters (vCenter or folder)
    :type obj: object
    :return: Dictionary containing a key -> value pair per datacenter
    :rtype: dict

    :Keyword Arguments:
        * *key* (``string``)
          String containing the attribute-name that shall be used as the dictionary-key. May be "rel_path" to construct a relative path, which is descriptive and unique containing all the folders (default). Make sure to choose a unique attribute, otherwise elements will overwrite each other.
        * *key_prepend* (``string``)
          String which should be prepended to all keys that are built within this function
    """

    if 'key' in kwargs and kwargs['key']: key = kwargs['key']
    else: key = "rel_path"
    if 'key_prepend' in kwargs and kwargs['key_prepend']: key_prepend = kwargs['key_prepend']
    else: key_prepend = ""

    #Go into root-folder if object has one
    if hasattr(obj,'rootFolder'):
        key_prepend = f"{obj.rootFolder.name}/"
        log.debug(f"We on the vcenter. Going into the rootFolder, prepending {key_prepend}")
        return get_dict(obj.rootFolder,key=key,key_prepend=key_prepend)
    
    elif 'Datacenter' in obj.childType:
        return vmware.vsphere.recurse_child_dict(obj,"vim.Datacenter",key,key_prepend=key_prepend)
    
    else:
        log.info(f"Could not find expected childType 'Datacenter' in {obj.childType}")
        return dict()


def get_list (obj,**kwargs):
    """
    Get all datacenters beneath the object and return a list. 
    This function is much faster than get_dict() when the vCenter-object is present (passed within *kwargs* or present as default)

    :param obj: The object within we shall search for datacenters (vCenter or folder)
    :type obj: object
    :return: List of objects
    :rtype: list

    :Keyword Arguments:
        * *vc_obj* (``object``)
          vCenter-object that was created by vmware.vsphere.get_content(). This will overwrite the object that was registered as default by vmware.vsphere.default()
    """
    vc = vmware.vsphere.get_vc_obj(kwargs)
    #Go into root-folder if object has one
    if hasattr(obj,'rootFolder'):
        log.debug(f"We on the vcenter. Going into the rootFolder")
        return get_list(obj.rootFolder,vc_obj=vc)
    
    elif 'Datacenter' in obj.childType:
        if vc: ret = vmware.vsphere.view.container(vc,obj,vim.Datacenter,recurse=True)
        else:
            ret = []
            for k,v in get_dict(obj).items():
                ret.append(v)
        
        return ret
    
    else:
        log.info(f"Could not find expected childType 'Datacenter' in {obj.childType}")
        return list()


def get (attr_name,attr_value,obj,**kwargs):
    """
    Get a specific datacenter identified by an attribute. Will only return the first object that matches

    :param attr_name: Name of the attribute that shall be used for selecting the object. Can also be "rel_path" to match a specific path within a folder-structure. Be aware, that this will trigger a 'get_dict' which may take a while.
    :type obj: string
    :param attr_value: Value which attr_name must contain
    :type obj: string
    :param obj: The object within we shall search for clusters (vCenter or folder)
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

    log.debug(f"Getting dc where {attr_name} is {attr_value}")

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


def is_datacenter (obj):
    """
    Check if passed object is a datacenter

    :param obj: The object
    :type obj: object
    :return: True if it is a datacenter, false if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.Datacenter')


def is_type (obj):
    """
    Check if passed object is a datacenter

    :param obj: The object
    :type obj: object
    :return: True if it is a datacenter, false if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.Datacenter')