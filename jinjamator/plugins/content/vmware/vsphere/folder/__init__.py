from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim


def is_folder (obj):
    """
    Check if passed object is a folder

    :param obj: The object
    :type obj: object
    :return: True if it is a folder, false if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.Folder')

def is_type (obj):
    """
    Check if passed object is a folder

    :param obj: The object
    :type obj: object
    :return: True if it is a folder, false if not 
    :rtype: bool
    """
    return vmware.vsphere.is_obj_type (obj,'vim.Folder')