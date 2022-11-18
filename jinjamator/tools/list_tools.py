from copy import deepcopy


def list_wo (haystack,needles):
    """
    Returns a list without the elements listed in `needles`

    :param haystack: The source list
    :type haystack: ``list``
    :param needles: The entries that shall be filtered out
    :type needles: ``list``
    :return: List without the elements in `needles`
    :rtype: ``list``
    """
    if isinstance(needles,str): needles = [needles]
    elif not isinstance(needles,list): return False
    haystack2 = deepcopy(haystack)
    for needle in needles: 
        if needle in haystack2: haystack2.remove(needle)

    return haystack2


def dict_wo (haystack,needles):
    """
    Returns a dictionary without the keys listed in `needles`

    :param haystack: The source dictionary
    :type haystack: ``dict``
    :param needles: The keys that shall be filtered out
    :type needles: ``list``
    :return: Dictionary without the elements in `needles`
    :rtype: ``dict``
    """
    if isinstance(needles,str): needles = [needles]
    elif not isinstance(needles,list): return False

    return {k: haystack[k] for k in haystack.keys() - needles}


def list2dict (list_orig,key_name,**kwargs):
    """
    Converts a list of dictionaries into a dictionary using the specified ``key_name`` as key


    :param list_orig: The original list
    :type list_orig: ``list``
    :param key_name: The name on the dictionary-item that should be used as a key
    :type key_name: ``str``
    :Keyword Arguments:
    * *duplicates* (``str``) --
        Tells the function how to deal with duplicates.
        Could be:
            - overwrite: Overwrites duplcate keys (default)
            - skip: Skips duplicate keys and just uses the first one
            - add: Creates the element and appends the index of the list

    :return: Dictionary with all list-elements using ``key_name`` as key
    :rtype: ``dict``
    """
    dodup = "overwrite"
    if "duplicates" in kwargs:
        if kwargs['duplicates'] == 'overwrite': dodup = "overwrite"
        elif kwargs['duplicates'] == 'skip': dodup = "skip"
        elif kwargs['duplicates'] == 'add': dodup = "add"
    
    ret = {}
    i = 1
    for elem in list_orig:
        if isinstance(elem,dict) or isinstance(elem,list):
            if key_name in elem:
                key = elem[key_name]
                
                if key in ret:
                    #Handle duplicates
                    if dodup == "skip":
                        continue
                    elif dodup == "add":
                        key = f"{key}_dup_{str(i)}"
                
                ret[key] = elem
        
        i += 1
    
    return ret


def get_by_value (key_name,value,iterable):
    """
    Returns the item of a list of dictionaries or a dictionary containing dictionaries, where the ``key`` has the value ``value``

    :param key_name: The name of the key
    :type key_name: ``str``
    :param value: The value the specified key has
    :type value: ``str``
    :param iterable: The dict/list in which the lookup should be done
    :type iterable: ``list``|``dict``
    :return: Dictionary where ``key`` has the value ``value``. Returns False of nothing was found
    :rtype: ``dict`` | ``bool``
    """
    if isinstance(iterable,list):
        for e in iterable:
            if key_name in e and e[key_name] == value:
                return e
    elif isinstance(iterable,dict):
        for e in iterable.values():
            if key_name in e and e[key_name] == value:
                return e
    
    return False
    