# Copyright 2021 Wilhelm Putz

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import re

host_cache = {}


def list(service_instance_content=None, cache=True):
    if not service_instance_content:
        service_instance_content = vmware.vsphere.get_content()
    if cache:
        if host_cache.get(id(service_instance_content)):
            log.debug("Using cached hosts")
            return host_cache.get(id(service_instance_content))

    log.debug("Getting all ESX hosts ...")
    host_view = service_instance_content.viewManager.CreateContainerView(
        service_instance_content.rootFolder, [vim.HostSystem], True
    )
    obj = [host for host in host_view.view]
    if cache:
        host_cache[id(service_instance_content)] = obj
    host_view.Destroy()
    return obj


def find(search, service_instance_content=None):
    rgx = re.compile(search)
    retval = []
    for host in list():
        if rgx.search(str(host)):
            retval.append(host)
    return retval


def get_dict (obj,**kwargs):
    """
    Get all hosts beneath the object and return a dictionary. 

    :param obj: The object within we shall search for hosts (datacenter or cluster)
    :type obj: object
    :return: Dictionary containing a key -> value pair per host
    :rtype: dict

    :Keyword Arguments:
        * *key* (``string``)
          String containing the attribute-name that shall be used as the dictionary-key. May be "rel_path" to construct a relative path, which is descriptive and unique containing all the folders (default). Make sure to choose a unique attribute, otherwise elements will overwrite each other.
    """
    if 'key' in kwargs and kwargs['key']: key = kwargs['key']
    else: key = "rel_path"
    
    if hasattr(obj,'hostFolder') and vmware.vsphere.datacenter.is_datacenter(obj):
        hostdict = dict()
        log.debug(f"This is a datacenter. We will collect standalone hosts")
        for n,h in vmware.vsphere.recurse_child_dict(obj.hostFolder,"vim.ComputeResource",key,key_prepend=obj.hostFolder.name).items():
            for ho_n,ho in get_dict(h,key=key).items():
                hostdict[ho_n] = ho
        return hostdict
    
    #Hosts within a cluster
    elif hasattr(obj,"host"):
        log.debug(f"Looking for hosts within cluster {obj.name}")
        return vmware.vsphere.get_objects_dict(obj.host,"vim.HostSystem")
    
    else:
        if hasattr(obj,"name"): log.info(f"Could not find hosts in {obj.name} ({type(obj)}")
        else: log.info(f"Could not find hosts in object ({type(obj)}")
        return {}


def get_list (obj,**kwargs):
    """
    Get all hosts beneath the object and return a list.
    This function is much faster than get_dict() when the vCenter-object is present (passed within *kwargs* or present as default)

    :param obj: The object within we shall search for hosts
    :type obj: object
    :return: List of objects
    :rtype: list

    :Keyword Arguments:
        * *vc_obj* (``object``)
          vCenter-object that was created by vmware.vsphere.get_content(). This will overwrite the object that was registered as default by vmware.vsphere.default()
    """
    vc = vmware.vsphere.get_vc_obj(kwargs)
    
    if vc: ret = vmware.vsphere.view.container(vc,obj,vim.HostSystem,recurse=True)
    else:
        ret = []
        for k,v in get_dict(obj).items():
            ret.append(v)
    
    return ret


def get (attr_name,attr_value,obj,**kwargs):
    """
    Get a specific host identified by an attribute. Will only return the first object that matches

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

    log.debug(f"Getting host where {attr_name} is {attr_value}")

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


def is_host (obj):
    """
    Check if passed object is a host

    :param obj: The object
    :type obj: object
    :return: True if it is a host, false if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.HostSystem')


def is_type (obj):
    """
    Check if passed object is a host

    :param obj: The object
    :type obj: object
    :return: True if it is a host, false if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.HostSystem')
