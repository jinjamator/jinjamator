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
    Get all datastore-clusters beneath the object and return a list.
    This function **requires** the vCenter-object to be present (passed within *kwargs* or present as default)

    :param obj: The object within we shall search for datastore-clusters
    :type obj: object
    :return: List of objects
    :rtype: list

    :Keyword Arguments:
        * *vc_obj* (``object``)
          vCenter-object that was created by vmware.vsphere.get_content(). This will overwrite the object that was registered as default by vmware.vsphere.default()
    """
    vc = vmware.vsphere.get_vc_obj(kwargs)
    
    ret = list()
    if vc: ret = vmware.vsphere.view.container(vc,obj,vim.StoragePod,recurse=True)
    else: vmware.vsphere.error_no_vc()
    
    return ret


def get (attr_name,attr_value,obj,**kwargs):
    """
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
    """
    #Rewrite id to _moId
    if attr_name == 'id': attr_name = "_moId"
    vc = vmware.vsphere.get_vc_obj(kwargs)

    log.debug(f"Getting datastore-cluster where {attr_name} is {attr_value}")

    if attr_name == 'rel_path':
        vmware.vsphere.error_no_vc()
    else:
        objects = get_list(obj,vc_obj=vc)
        
        for o in objects:
            if hasattr(o,attr_name):
                if getattr(o,attr_name) == attr_value:
                    return o
    
    return False


def is_datastore_cluster (obj):
    """
    Check if passed object is a datastore-cluster

    :param obj: The object
    :type obj: object
    :return: True if it is a datastore-cluster, false if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.StoragePod')


def is_type (obj):
    """
    Check if passed object is a datastore-cluster

    :param obj: The object
    :type obj: object
    :return: True if it is a datastore-cluster, false if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.StoragePod')


def get_vms (obj,**kwargs):
    """
    Get a list of all VMs using the datastore-cluster

    :param obj: The datastore-cluster-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    """
    ret = list()
    if is_datastore_cluster(obj):
        for ds in vmware.vsphere.datastore.get_list(obj):
            ret = ret + vmware.vsphere.datastore.get_vms(ds)
        
        return ret
    else:
        log.warning(f"Object is not a datastore-cluster: {type(obj)}")
    
    return ret

def get_datastores (obj,**kwargs):
    """
    Get a list of all datastore within the datastore-cluster

    :param obj: The datastore-cluster-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    """
    ret = list()
    if is_datastore_cluster(obj):
        ret = vmware.vsphere.datastore.get_list(obj)       
    else:
        log.warning(f"Object is not a datastore-cluster: {type(obj)}")
    
    return ret
