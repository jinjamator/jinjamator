vmware.vsphere.view
===============================================

.. toctree::
    :maxdepth: 1



.. py:function:: vmware.vsphere.view.container(vc, obj, search_type, **kwargs):

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
    


