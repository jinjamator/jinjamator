from pyVmomi import vim
import re


def list(content=None):
    if not content:
        content = vmware.vsphere.get_content()
    vm_view = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.VirtualMachine], True
    )
    obj = [vm for vm in vm_view.view]
    vm_view.Destroy()
    return obj


def list_names(content=None):
    return [vm.name for vm in list(content)]


def find(search, return_type="obj", service_instance_content=None):
    rgx = re.compile(search)
    retval = []
    for obj in list():
        if rgx.search(str(obj.name)):
            if return_type == "name":
                retval.append(obj.name)
            elif return_type == "obj":
                retval.append(obj)
            else:
                retval.append(obj)
    return retval
