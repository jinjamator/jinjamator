from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim
from collections import Counter


def get_dict (obj,**kwargs):
    """
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
    """
    if 'key' in kwargs and kwargs['key']: key = kwargs['key']
    else: key = "rel_path"
    if 'key_prepend' in kwargs and kwargs['key_prepend']: key_prepend = kwargs['key_prepend']
    else: key_prepend = ""

    #Go into root-folder if object has one
    if hasattr(obj,'vmFolder'):
        key_prepend = f"{obj.vmFolder.name}/"
        log.debug(f"We are in the datacenter. Going to vmFolder, prepending {key_prepend}")
        return get_dict(obj.vmFolder,key=key,key_prepend=key_prepend)
    
    ##########################
    # TODO:
    # Get VM's within cluster
    ##########################
    elif hasattr (obj,'childType') and 'VirtualMachine' in obj.childType:
        return vmware.vsphere.recurse_child_dict(obj,"vim.VirtualMachine",key,key_prepend=key_prepend)
    
    else:
        log.info(f"Could not find expected childType 'VirtualMachine' in {obj.childType}")
        return dict()


def get_list (obj,**kwargs):
    """
    Get all VMs beneath the object and return a list.
    This function is much faster than get_dict() when the vCenter-object is present (passed within *kwargs* or present as default)

    :param obj: The object within we shall search for VMs
    :type obj: object
    :return: List of objects
    :rtype: list

    :Keyword Arguments:
        * *vc_obj* (``object``)
          vCenter-object that was created by vmware.vsphere.get_content(). This will overwrite the object that was registered as default by vmware.vsphere.default()
    """
    vc = vmware.vsphere.get_vc_obj(kwargs)
    
    if vc: ret = vmware.vsphere.view.container(vc,obj,vim.VirtualMachine,recurse=True)
    else:
        ret = []
        for k,v in get_dict(obj).items():
            ret.append(v)
    
    return ret


def get (attr_name,attr_value,obj,**kwargs):
    """
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
    """
    #Rewrite id to _moId
    if attr_name == 'id': attr_name = "_moId"
    vc = vmware.vsphere.get_vc_obj(kwargs)

    log.debug(f"Getting vm where {attr_name} is {attr_value}")

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


def get_datastores (obj):
    """
    Get a list of all datastores that are used by the VM

    :param obj: The VM-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    """
    if is_type(obj):
        if hasattr(obj,'datastore'):
            return [item for item in obj.datastore]
    else:
        log.warning(f"Object is not a vm: {type(obj)}")
    
    return list()


def get_datastore_clusters (obj):
    """
    Get a list of all datastore-clusters that are used by the VM

    :param obj: The VM-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    """
    ret = list()
    for ds in get_datastores(obj):
        if vmware.vsphere.datastore.is_clustered(ds):
            ret.append(vmware.vsphere.datastore.get_datastore_cluster(ds))
    
    return vmware.vsphere.list_make_unique(ret)


def get_respool (obj):
    """
    Get the respool in which the VM resides

    :param obj: The VM-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    """
    if is_type(obj):
        if hasattr(obj,'resourcePool'):
            return obj.resourcePool
    else:
        log.warning(f"Object is not a vm: {type(obj)}")
    
    return list()


def get_networks (obj):
    """
    Get a list of all networks (portgroups) that are used by the VM

    :param obj: The VM-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    """
    if is_type(obj):
        if hasattr(obj,'network'):
            return [item for item in obj.network]
    else:
        log.warning(f"Object is not a vm: {type(obj)}")
    
    return list()


def get_cluster (obj):
    """
    Get the cluster which hosts the VM

    :param obj: The VM-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    """
    cluster = vmware.vsphere.get_first_parent_type (obj.resourcePool,'vim.ClusterComputeResource')
    if cluster:
        return cluster
    else:
        standalone = vmware.vsphere.get_first_parent_type (obj.resourcePool,'vim.ComputeResource')
        return standalone


def get_host (obj):
    """
    Get the host which hosts the VM

    :param obj: The VM-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    """
    if is_type(obj):
        if hasattr(obj,'runtime') and hasattr(obj.runtime,'host'):
            return obj.runtime.host
    else:
        log.warning(f"Object is not a vm: {type(obj)}")
    
    return False


def get_folder (obj):
    """
    Get the parent folder in which the VM is situated

    :param obj: The VM-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    """
    if is_type(obj):
        if hasattr(obj,'parent') and vmware.vsphere.folder.is_type(obj.parent):
            return obj.parent
    else:
        log.warning(f"Object is not a vm: {type(obj)}")
    
    return False


def is_vm (obj):
    """
    Check if passed object is a VM

    :param obj: The object
    :type obj: object
    :return: True if it is a VM, false if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.VirtualMachine')


def is_type (obj):
    """
    Check if passed object is a VM

    :param obj: The object
    :type obj: object
    :return: True if it is a VM, false if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.VirtualMachine')
