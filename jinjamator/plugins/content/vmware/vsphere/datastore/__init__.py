from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim

def get_dict (obj,**kwargs):
    """
    This function is not yet implemented
    """
    
    if 'key' in kwargs and kwargs['key']: key = kwargs['key']
    else: key = "rel_path"
    
    ret = dict()
    vmware.vsphere.error_no_vc()
    return dict()


def get_list (obj,**kwargs):
    """
    Get all datastores beneath the object and return a list.
    This function **requires** the vCenter-object to be present (passed within *kwargs* or present as default)

    :param obj: The object within we shall search for datastores
    :type obj: object
    :return: List of objects
    :rtype: list

    :Keyword Arguments:
        * *vc_obj* (``object``)
          vCenter-object that was created by vmware.vsphere.get_content(). This will overwrite the object that was registered as default by vmware.vsphere.default()
    """
    vc = vmware.vsphere.get_vc_obj(kwargs)
    
    ret = list()
    if vc: ret = vmware.vsphere.view.container(vc,obj,vim.Datastore,recurse=True)
    else: vmware.vsphere.error_no_vc()
    
    return ret


def get (attr_name,attr_value,obj,**kwargs):
    """
    Get a specific datastore identified by an attribute. Will only return the first object that matches

    :param attr_name: Name of the attribute that shall be used for selecting the object. Using "rel_path" will fail and generate an error
    :type obj: string
    :param attr_value: Value which attr_name must contain
    :type obj: string
    :param obj: The object within we shall search for the datastore
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

    log.debug(f"Getting datastore where {attr_name} is {attr_value}")

    if attr_name == 'rel_path':
        vmware.vsphere.error_no_vc()
    else:
        objects = get_list(obj,vc_obj=vc)
        
        for o in objects:
            if hasattr(o,attr_name):
                if getattr(o,attr_name) == attr_value:
                    return o
    
    return False


def is_datastore (obj):
    """
    Check if passed object is a datastore

    :param obj: The object
    :type obj: object
    :return: True if it is a datastore, false if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.Datastore')


def is_type (obj):
    """
    Check if passed object is a datastore

    :param obj: The object
    :type obj: object
    :return: True if it is a datastore, false if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.Datastore')


def get_vms (obj,**kwargs):
    """
    Get a list of all VMs using the datastore

    :param obj: The datastore-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    """
    if is_datastore(obj):
        if hasattr(obj,'vm'):
            return [item for item in obj.vm]
    else:
        log.warning(f"Object is not a datastore: {type(obj)}")
    
    return list()

def get_host_mounts (obj):
    """
    Get a list of the host mountpoints

    :param obj: The datastore-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    """
    if is_datastore(obj):
        if hasattr(obj,'host'):
            return [item for item in obj.host]
    else:
        log.warning(f"Object is not a datastore: {type(obj)}")
    
    return list()


def get_hosts (obj):
    """
    Get a list of all hosts that are mounting the datastore

    :param obj: The datastore-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    """
    ret = list()
    for mount in get_host_mounts(obj):
        if hasattr(mount,'key') and vmware.vsphere.host.is_host(mount.key):
            ret.append(mount.key)
        elif not hasattr(mount,'key'):
            log.warning(f"Mountpoint has no key")
        else: 
            log.warning(f"Mountpoint is not a host: {type(mount.key)}")
    
    return ret


def is_clustered (obj):
    """
    Check if datastore is part of a datastore-cluster

    :param obj: The datastore-object
    :type obj: object
    :return: True if the datastore is part of a cluster, False if not
    :rtype: bool
    """
    if is_datastore(obj):
        if hasattr(obj,'parent') and vmware.vsphere.datastore.cluster.is_datastore_cluster(obj.parent):
            return True
        else:
            log.debug(f"Datastore {obj.name} is not clustered")
    else:
        log.warning(f"Object {obj.name} is not a datastore: {type(obj)}")
    
    return False


def get_datastore_cluster (obj):
    """
    Get the datastore-cluster the datastore is part of

    :param obj: The datastore-object
    :type obj: object
    :return: datastore-cluster object. Returns "False" if it is not clustered
    :rtype: bool
    """
    if is_clustered(obj):
        return obj.parent
    else:
        return False