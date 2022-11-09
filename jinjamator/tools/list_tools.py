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