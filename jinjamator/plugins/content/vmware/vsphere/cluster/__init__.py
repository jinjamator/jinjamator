from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim
from collections import Counter

def get_dict (obj,**kwargs):
    """
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
    """
    
    if 'key' in kwargs and kwargs['key']: key = kwargs['key']
    else: key = "rel_path"

    if not 'cluster' in kwargs and not 'standalone' in kwargs:
        kwargs['cluster'] = True
        kwargs['standalone'] = True
    
    ret = dict()
    if hasattr(obj,"hostFolder"):
        if 'ComputeResource' in obj.hostFolder.childType:
            if 'cluster' in kwargs and kwargs['cluster']: ret.update(vmware.vsphere.recurse_child_dict(obj.hostFolder,"vim.ClusterComputeResource",key))
            if 'standalone' in kwargs and kwargs['standalone']: ret.update(vmware.vsphere.recurse_child_dict(obj.hostFolder,"vim.ComputeResource",key))
            return ret

        else:
            log.info(f"Could not find expected childType 'ComputeResource' in {obj.hostFolder.childType}")
            return dict()
    else:
        return dict()
    

def get_list (obj,**kwargs):
    """
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
    """
    if not 'cluster' in kwargs and not 'standalone' in kwargs:
        kwargs['cluster'] = True
        kwargs['standalone'] = True
    
    vc = vmware.vsphere.get_vc_obj(kwargs)
    
    ret = list()
    if vc:
        if 'cluster' in kwargs and kwargs['cluster']: ret = ret + vmware.vsphere.view.container(vc,obj,vim.ClusterComputeResource,recurse=True)
        if 'standalone' in kwargs and kwargs['standalone']: ret = ret + vmware.vsphere.view.container(vc,obj,vim.ComputeResource,recurse=True)
        return ret
    else:
        if hasattr(obj,"hostFolder"):
            if 'ComputeResource' in obj.hostFolder.childType:
                if 'cluster' in kwargs and kwargs['cluster']: ret.append(vmware.vsphere.recurse_child_list(obj.hostFolder,"vim.ClusterComputeResource"))
                if 'standalone' in kwargs and kwargs['standalone']: ret.append(vmware.vsphere.recurse_child_list(obj.hostFolder,"vim.ComputeResource"))
                return ret

            else:
                log.info(f"Could not find expected childType 'ComputeResource' in {obj.hostFolder.childType}")
                return list()
        else:
            log.info(f"Passed object does not contain a hostFolder")
            return list()


def get (attr_name,attr_value,obj,**kwargs):
    """
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
    """
    #Rewrite id to _moId
    if attr_name == 'id': attr_name = "_moId"
    vc = vmware.vsphere.get_vc_obj(kwargs)

    log.debug(f"Getting cluster where {attr_name} is {attr_value}")

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
    
    log.debug(f"Could not find object matching the given attributes {attr_name} : {attr_value}")
    return False


def get_hosts (obj):
    """
    Get a list of all hosts in the cluster

    :param obj: The cluster-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    """
    return vmware.vsphere.host.get_list(obj)

def get_datastores (obj):
    """
    Get a list of all datastores in the cluster

    :param obj: The cluster-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    """
    if is_type(obj):
        if hasattr(obj,'datastore'):
            return [item for item in obj.datastore]
    else:
        log.warning(f"Object is not a cluster: {type(obj)}")
    
    return list()

def get_datastore_clusters (obj):
    """
    Get a list of all datastore-clusters in the cluster

    :param obj: The cluster-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    """
    ret = list()
    for ds in get_datastores(obj):
        if vmware.vsphere.datastore.is_clustered(ds):
            ret.append(vmware.vsphere.datastore.get_datastore_cluster(ds))
    
    return vmware.vsphere.list_make_unique(ret)

def get_respools (obj):
    """
    Get a list of all resource-pools in the cluster

    :param obj: The cluster-object
    :type obj: object
    :return: List of objects 
    :rtype: list
    """
    if is_type(obj):
        if hasattr(obj,'resourcePool'):
            return vmware.vsphere.cluster.respool.get_list(obj)
    else:
        log.warning(f"Object is not a resourcePool: {type(obj)}")
    
    return list()

def is_cluster (obj):
    """
    Check if passed object is a cluster

    :param obj: The object
    :type obj: object
    :return: True if it is a cluster, false if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.ClusterComputeResource')

def is_type (obj):
    """
    Check if passed object is a cluster

    :param obj: The object
    :type obj: object
    :return: True if it is a cluster, false if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.ClusterComputeResource')
