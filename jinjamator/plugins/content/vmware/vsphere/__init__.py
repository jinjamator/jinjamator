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
#
# based on https://github.com/vmware/pyvmomi-community-samples
#

from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim, vmodl
from collections.abc import Iterable
from collections import Counter

vsphere_connection_pool = {}


def get_content(service_instance=None, cache=True):
    """
    Get the content of the service_instance
    It is highly recommended to use vmware.vsphere.default() on the return value

    :param service_instance: The service_instance created by connect()
    :type service_instance: object
    :param cache: Write object to cache if set to True
    :type cache: bool
    :return: Content object
    :rtype: object
    """
    if cache:
        _cfg = _jinjamator.configuration
        if vsphere_connection_pool.get(_cfg["vsphere_host"]):
            if (
                vsphere_connection_pool[_cfg["vsphere_host"]]
                .get(_cfg["vsphere_username"], {})
                .get("content")
            ):
                log.debug("Using cached content")
                return (
                    vsphere_connection_pool[_cfg["vsphere_host"]]
                    .get(_cfg["vsphere_username"], {})
                    .get("content")
                )

    if not service_instance:
        service_instance = connect()
    content = service_instance.RetrieveContent()
    if cache:
        vsphere_connection_pool[_cfg["vsphere_host"]][_cfg["vsphere_username"]][
            "content"
        ] = content
    return content


def get_obj(vimtype, name, content=None):
    if not content:
        content = get_content()
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True
    )
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj


def connect(host=None, username=None, password=None, cache=True):
    """
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
    """
    _cfg = _jinjamator.configuration
    for param in ["vsphere_host", "vsphere_username", "vsphere_password"]:
        if locals().get(param):
            _cfg[param] = locals()[param]
        if not _cfg[param]:
            _jinjamator.handle_undefined_var(param)
    if cache:
        if vsphere_connection_pool.get(_cfg["vsphere_host"]):

            if vsphere_connection_pool[_cfg["vsphere_host"]].get(
                _cfg["vsphere_username"]
            ):
                log.debug(
                    f'Using cached connection to VSphere host {_cfg["vsphere_host"]}'
                )
                return vsphere_connection_pool[_cfg["vsphere_host"]][
                    _cfg["vsphere_username"]
                ]["service_instance"]

    service_instance = SmartConnectNoSSL(
        host=_cfg["vsphere_host"],
        user=_cfg["vsphere_username"],
        pwd=_cfg["vsphere_password"],
        port=443,
    )
    if service_instance:
        log.debug(f"Connected VSphere host {_cfg['vsphere_host']}")
    else:
        raise Exception(f"Cannot connect VSphere host {_cfg['vsphere_host']}")
    if cache:

        vsphere_connection_pool[_cfg["vsphere_host"]] = {
            _cfg["vsphere_username"]: {"service_instance": service_instance}
        }
    return service_instance


def is_obj_type (obj,type_name):
    """
    Check if passed object is matching the passed type. This is currently not a strict match as "type_name" is a string and needs only to be a subset of str(type(obj))

    :param obj: The object
    :type obj: object
    :param type_name: The type
    :type type_name: string
    :return: True or False 
    :rtype: bool
    """
    if isinstance(obj,object):
        if type_name in str(type(obj)):
            return True
    
    return False


def recurse_child_dict (obj,childType,key,**kwargs):
    """
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
    """
    if 'key_prepend' in kwargs and kwargs['key_prepend']: key_prepend = kwargs['key_prepend']
    else: key_prepend = ""

    ret = dict()
    if key == 'rel_path':
        key = 'name'
        key_true = 'rel_path'
    else: key_true = key

    log.debug(f"Recursing childs of {obj.name} into a dict using '{key_true}' as key")
    if hasattr(obj,"childType") and hasattr(obj,"childEntity"):
        log.debug(f"- Current object has childs")
        
        for child in obj.childEntity:
            log.debug(f"-- Processing child {child.name} ({type(child)})")
            
            if vmware.vsphere.folder.is_folder(child):
                log.debug(f"-- Child {child.name} is a folder")
                childs = recurse_child_dict(child,childType,key_true)
                for k,o in childs.items():
                    log.debug(f"--- Adding recursed {k} to returning dict. Prepending {key_prepend}")
                    if key_true == 'rel_path': ret[f"{key_prepend}{getattr(child,key)}/{k}"] = o
                    else: ret[f"{key_prepend}{k}"] = o
            elif is_obj_type(child,childType):
                log.debug(f"--- Adding {getattr(child,key)} to returning dict")
                ret[f'{key_prepend}{getattr(child,key)}'] = child
            else:
                if hasattr(child,"childType") and hasattr(child,key):
                    log.debug(f"--- Child {getattr(child,key)} does not match the expected childType (is: {child.childType} / expected: {childType})")
                elif hasattr(child,key):
                    log.debug(f"--- Child {getattr(child,key)} does not have a childType")
                else:
                    log.debug(f"--- Child is somewhat corrupt: {child}")
        
    return ret


def recurse_child_list (obj,childType,**kwargs):
    """
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
    """
    ret = list()
    log.debug(f"Recursing childs of {obj.name} into a list")
    if hasattr(obj,"childType") and hasattr(obj,"childEntity"):
        log.debug(f"- Current object has childs")
        
        for child in obj.childEntity:
            log.debug(f"-- Processing child {child.name} ({type(child)})")
            
            if vmware.vsphere.folder.is_folder(child):
                log.debug(f"-- Child {child.name} is a folder")
                childs = recurse_child_list(child,childType)
                for o in childs:
                    log.debug(f"--- Adding recursed {o.name} to returning list")
                    ret.append(o)
            elif is_obj_type(child,childType):
                log.debug(f"--- Adding {child.name} to returning list")
                ret.append(child)
            else:
                if hasattr(child,"childType") and hasattr(child,'name'):
                    log.debug(f"--- Child {child.name} does not match the expected childType (is: {child.childType} / expected: {childType})")
                elif hasattr(child,'name'):
                    log.debug(f"--- Child {child.name} does not have a childType")
                else:
                    log.debug(f"--- Child is somewhat corrupt: {child}")
        
    return ret


def recurse_child (obj,childType,key=False):
    """
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

    """
    if key: return recurse_child_dict(obj,childType,key)
    else: return recurse_child_list(obj,childType)


def get_objects_dict (obj,obj_type='*',**kwargs):
    """
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
    """
    if 'key' in kwargs and kwargs['key']: key = kwargs['key']
    else: key = "name"
    
    ret = dict()
    for o in obj:
        if is_obj_type(o,obj_type) or obj_type == '*':
            log.debug(f"Getting object {o} using {key} as key")
            if hasattr(o,key):
                ret[getattr(o,key)] = o
        else:
            log.debug(f"Ignoring object {o} because type {type(obj)} does not match expected {obj_type}")
    
    return ret


def get_objects_list (obj,obj_type='*'):
    """
    Get all objects within an an object-attribute and return them as list
    Can filter by object-type if specified

    :param obj: The object-attribute containing a list of entries
    :type obj: list
    :param obj_type: Object-type that should be returned. Default is "*" to disable filtering
    :type obj_type: string
    :return: List of matching items
    :rtype: list
    """
    ret = list()
    log.debug(f"Getting object_list in {obj}")
    objects = get_objects_dict(obj,obj_type)
    log.debug(f"-- Found {len(objects)} objects, starting iter")
    for k,v in objects.items():
        ret.append(v)
    log.debug(f"Done getting object_list in {obj}")

    return ret


def recurse_objects_dict (obj,attr_name,**kwargs):
    """
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
    """
    ret = dict()
    if 'key' in kwargs and kwargs['key']: key = kwargs['key']
    else: key = "name"
    if 'key_prepend' in kwargs and kwargs['key_prepend']: key_prepend = kwargs['key_prepend']
    else: key_prepend = ""

    if hasattr(obj,attr_name):
        log.debug(f"Recursing object {getattr(obj,attr_name)} (attr {attr_name})")
        if isinstance(getattr(obj,attr_name),Iterable):
            log.debug(f"- Object is iterable")
            obs = get_objects_list(getattr(obj,attr_name),'*')

            log.debug(f"-- Got {len(obs)} objects in the list")
            if len(obs) > 0:
                for i in obs:
                    log.debug(f"--- Iterating through {i}")
                    child_obj = recurse_objects_dict(i,attr_name,key=key)
                    log.debug(f"--- Got {len(child_obj)} objects we need to process.\n{child_obj}")
                    for k,o in child_obj.items():
                        log.debug(f"---- Preparing {key} for return")
                        if key == 'rel_path': ret[f"{key_prepend}{getattr(i,'name')}/{k}"] = o
                        else: ret[f'{k}'] = o
                            
            else:
                log.debug(f"--- No items in list, returning myself")
                if key == 'rel_path': ret[f"{key_prepend}{getattr(obj,'name')}"] = obj
                else: ret[f'{getattr(obj,"name")}'] = obj

        else:
            log.debug(f"- Object is not iterable. Going in and prepending its name ({getattr(obj,attr_name).name})")
            return recurse_objects_dict(getattr(obj,attr_name),attr_name,key_prepend=f"{getattr(obj,attr_name).name}/",key=key)

    else:
        log.debug(f"Object does not have attribute {attr_name}")
        if key == 'rel_path': ret[f"{key_prepend}{getattr(obj,'name')}"] = obj
        else: ret[getattr(obj,key)] = obj
    
    return ret


def recurse_objects_list (obj,attr_name,**kwargs):
    """
    Recurse through all objects that are contained in the given attribute (attr_name).

    :param obj: The object
    :type obj: object
    :param attr_name: The name of the attribute that shall be recursed
    :type attr_name: string
    :return: List of matching items
    :rtype: list

    :Keyword Arguments:
        Currently none
    """
    ret = list()
    for o in recurse_objects_dict(obj,attr_name).values():
        ret.append(o)
    
    return ret


def get_absolute_path (obj):
    """
    Gets the absolute path from the given object as long as there is a parent

    :param obj: The object
    :type obj: object
    :return: String of all parents seperated by /
    :rtype: string
    """
    if has_parent(obj):
        if hasattr(obj,"name"): 
            ppath = f"{get_absolute_path (obj.parent)}"
            if len(ppath) > 0: path = f"{ppath}/{obj.name}"
            else: path = obj.name
        else: path = f"{get_absolute_path (obj.parent)}"
    else:
        if hasattr(obj,"name"): path = obj.name
        else: path = ""
    
    return path


def has_parent (obj):
    """
    Checks if the object has a parent

    :param obj: The object
    :type obj: object
    :return: True or False
    :rtype: bool
    """
    if hasattr(obj,'parent') and isinstance(obj,object):
        return True
    else:
        return False


def parent_is_type (obj,parent_type):
    """
    Checks if the parent matches the given type

    :param obj: The object
    :type obj: object
    :param parent_type: The expected type of the parent
    :type parent_type: string
    :return: True or False
    :rtype: bool
    """
    if has_parent(obj):
        if is_obj_type(obj.parent,parent_type):
            return True
    return False


def get_id (obj):
    """
    Get the ID (_moId) of the object

    :param obj: The object
    :type obj: object
    :return: The ID-string (_moId). Empty string if there is no ID
    :rtype: string
    """
    if isinstance(obj,object):
        if hasattr(obj,'_moId'):
            return obj._moId
    
    return ""


def get_first_parent_type (attr,parent_type):
    """
    Gets the first parent of an attribute that matches the given type

    :param obj: The attribute-object
    :type obj: object
    :param obj: The type of the object
    :type obj: string
    :return: First parent-object that matches the type
    :rtype: object
    """
    return recurse_parent_if_type_not (attr,parent_type)


def recurse_parent_if_type_not (obj,parent_type):
    """
    Recurse through parents of the object until the parent type is the given type or no parent is left

    :param obj: The object
    :type obj: object
    :param obj: The type of the parent object to look out for
    :type obj: string
    :return: First parent-object that matches the type
    :rtype: object
    """
    if parent_is_type(obj,parent_type):
        #return the parent if it matches the type
        return obj.parent
    elif has_parent(obj):
        #Parent is present but not the correct type
        #recurse through
        return recurse_parent_if_type_not(obj.parent,parent_type)
    else:
        #There is no parent
        return False


def is_vc (obj):
    """
    Check if passed object is a vCenter

    :param obj: The object
    :type obj: object
    :return: True if it is a vCenter, False if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.ServiceInstanceContent')


def is_type (obj):
    """
    Check if passed object is a vCenter

    :param obj: The object
    :type obj: object
    :return: True if it is a vCenter, False if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.ServiceInstanceContent')


def default (obj):
    """
    Set the object as default vCenter-object (highly recommended)

    :param obj: The object
    :type obj: object
    :return: Returns the object again
    :rtype: object
    """
    _jinjamator.configuration['default_vc'] = obj


def get_vc_obj (kwargs):
    """
    Gets the vc_object from passed kwargs or the default set by vmware.vsphere.default()

    :param kwargs: kwargs passed into the parent function
    :type kwargs: dict
    :return: vCenter-object or False
    :rtype: object
    """
    if 'vc_obj' in kwargs and vmware.vsphere.is_vc(kwargs['vc_obj']): vc = kwargs['vc_obj']
    elif vmware.vsphere.is_vc(_jinjamator.configuration['default_vc']): vc = _jinjamator.configuration['default_vc']
    else: vc = False

    return vc


def error_no_vc (**kwargs):
    """
    Generates an error (function for lazy men)

    :return: nothing
    :rtype: none
    """
    log.warning(f"Cannot complete operation without vcenter-object. Function not available or not implemented")


def list_make_unique (elements):
    """
    Removes duplicates from a list of elements

    :param elements: List of elements
    :type elements: list
    :return: deduplicated list
    :rtype: list
    """
    return [item for item in Counter(elements)]


########################################
#Property-Collector Example
#https://medium.com/@maciej.wawrzynczuk/collecting-data-from-vcenter-with-python-pyvmomi-and-propertycollector-the-fast-way-a915ab4efd32
#
#print("================= Filtered VMs =================")
#vm_view = vmware.vsphere.view.container_obj(vc,dc_net,vim.VirtualMachine,recurse=True)
#vms = vmware.vsphere.search(vm_view,vim.VirtualMachine,path_set=None)
##vms = vmware.vsphere.search(vm_view,vim.VirtualMachine,path_set=["name"])
#
#for vm in vms:
#    pprint(vm)
#    print(type(vm.propSet))
#    print(f"Name is: {vm.propSet['config'].name}")
#    break
#
#def search (view,obj_type,path_set=None,**kwargs):
#    vc = vmware.vsphere.get_vc_obj(kwargs)
#
#    log.debug(f"Building TraversalSpec")
#    ts = vmodl.query.PropertyCollector.TraversalSpec()
#    ts.name = 'traverseEntries'
#    ts.path = 'view'
#    ts.skip = False
#    ts.type = view.__class__
#    
#    log.debug(f"Building ObjectSpec")
#    os = vmodl.query.PropertyCollector.ObjectSpec()
#    os.obj = view
#    os.skip = True
#    os.selectSet = [ts]   
#
#    log.debug(f"Building PropertySpec")
#    ps = vmodl.query.PropertyCollector.PropertySpec()
#    ps.type = obj_type
#    if not path_set:
#        ps.all = True
#    ps.pathSet = path_set
#
#    log.debug(f"Building FilterSpec")
#    fs = vmodl.query.PropertyCollector.FilterSpec()
#    fs.objectSet = [os]
#    fs.propSet = [ps]
#
#    log.debug(f"Building propertyCollector")
#    collector = vc.propertyCollector
#    log.debug(f"Retrieving properties")
#    props = collector.RetrieveProperties([fs])
#
#    return props