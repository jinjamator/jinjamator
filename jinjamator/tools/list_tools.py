from copy import deepcopy
import re


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


def get_by_key_regex (key_re,iterable,ignorecase=False):
    """
    Returns a dict of items where the key matches the regex given

    :param key_re: The regex to look for
    :type key_re: ``str``
    :param iterable: The dict in which the lookup should be done
    :type iterable: ``dict``
    :Keyword Arguments:
    * *ignorecase* (``bool``) --
        Ignore case sensivity in regex.
        False by default
    :return: Dictionary where the keys match the regex. Returns empty dict if nothing matched
    :rtype: ``dict``
    """
    if ignorecase == False: reg = re.compile(key_re)
    else: reg = re.compile(key_re,re.IGNORECASE)

    ret = {}
    for k,v in iterable.items():
        if reg.match(k): ret[k] = v
    
    return ret


def try_to_fill (base,values):
    """
    Tries to fill the ``base`` dict with values from ``values``
    Will iterate over ``base`` looking for keys in ``values`` - if the key exist, overwrite base key with values key

    :param base: The base dict
    :type base: ``dict``
    :param values: The values dict
    :type values: ``dict``
    :return: ``base`` dictionary with values of ``values`` dict if key existed
    :rtype: ``dict``
    """
    iter_list = base.keys()
    for idx in iter_list:
        try: base[idx] = values[idx]
        except: pass
    
    return base


def update_empty_values (first,second,create_keys=True):
    """
    Will update empty values of keys in ``first`` dict with the values of ``second`` dict
    Empty is an empty string ("") or ``None``
    If ``create_keys`` is set to ``True``, keys that exist in ``second`` but not in ``first`` will be created

    :param first: First dict
    :type first: ``dict``
    :param second: Second dict
    :type second: ``dict``
    :param create_keys: Create keys if they are present in ``second`` buit not in ``first``. Default: True
    :type create_keys: ``boolean``
    :return: ``dict`` whith updated values
    :rtype: ``dict``
    """
    #If we create new keys instead of only updating existing ones, merge the dicts, preserving the values of first
    if create_keys == True: dict_res = second | first
    else: dict_res = first
    
    #Check each key of second and update the value if
    # - key exists
    # - and the value is an empty string or none
    for k,v in second.items():
        if k in dict_res.keys():
            #An empty string or None counts as empty
            if dict_res[k] == "" or dict_res[k] == None:
                dict_res[k] = v
    
    return dict_res