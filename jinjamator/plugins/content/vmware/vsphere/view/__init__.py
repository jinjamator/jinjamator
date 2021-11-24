from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim


def container (vc,obj,search_type,**kwargs):
    """
    Create a container-view of the object and get a list of all containing objects that are matching search_type

    :param vc: The vCenter-object in which the container-view shall be created
    :type obj: object
    :param obj: The object
    :type obj: object
    :param search_type: List of types that should be matching (i.e vim.Folder). Will convert itself into a list if a single element is given
    :type obj: list
    :return: List of matching items
    :rtype: list

    :Keyword Arguments:
        * *recurse* (``bool``)
          If set to "True" recursion through childs is enabled. Default is False
    """
    if 'recurse' in kwargs: recurse = kwargs['recurse']
    else: recurse = False

    if not isinstance(search_type,list): search_type = [search_type]
    log.debug(f"Creating view for {search_type}")
    view = vc.viewManager.CreateContainerView(obj, search_type, recurse)
    ret = [item for item in view.view]
    view.Destroy()

    return ret

#def container_obj (vc,obj,search_type,**kwargs):
#    if 'recurse' in kwargs: recurse = kwargs['recurse']
#    else: recurse = False
#
#    if not isinstance(search_type,list): search_type = [search_type]
#    log.debug(f"Creating view for {search_type}")
#    view = vc.viewManager.CreateContainerView(obj, search_type, recurse)
#
#    return view
#
