import tempfile
from random import random
import hashlib

file_temp_tempdirs = []

class tmpfile:
    name = ""

    def __init__(self,name):
        self.name = name


def dir(**kwargs):
    """
    Create a temporary directory

    :return: tempfile.TemporaryDirectory() object
    :rtype: ``object``
    """
    global file_temp_tempdirs
    #if isinstance(tmpdirs,list): print("Found tmpdirs")
    #if not hasattr(_jinjamator.configuration,"tmpdirs"):
        #setattr(_jinjamator.configuration,"tmpdirs",[])
        #_jinjamator.configuration['tmpdirs'] = []
    tmpdir = tempfile.TemporaryDirectory(**kwargs)
    #Keep the object alive
    #_jinjamator.configuration['tmpdirs'].append(tmpdir)
    file_temp_tempdirs.append(tmpdir)
    return tmpdir


def name (temp_obj):
    """
    Gets the name (== the path) of the temp-directory
    Returns False if there is not temp_dir

    :param temp_obj: The temp object (created by temp_dir) from which the name should be extracted
    :type temp_obj: ``object``
    :return: Name of the temp_dir (== the path), False if temp_obj was not a valid object or had no `name` attribute
    :rtype: ``string``, ``bool``
    """
    if isinstance(temp_obj,object) and hasattr(temp_obj,"name"):
        return temp_obj.name
    else:
        return False


def file (**kwargs):
    """
    Returns an object for a tempfile
    Currently only the `name` attribute is populated

    :keyword str name: The filename that should be used. Will generate one of none given
    :keyword object,str dir: The temp-dir that should be used to store the file. Can be an existing path (string) or a temp_dir() object
    :return: A `tmpfile` object. Use the `name` attribute to get the filename
    :rtype: ``object``
    """
    if "name" in kwargs:
        filename = kwargs['name']
    else:
        rnd = str(random()).encode('utf-8')
        filename = hashlib.md5(rnd).hexdigest()
    
    if "dir" in kwargs:
        #if dir is a temp_dir object
        if name(kwargs['dir']): 
            #extract the name from the object
            tmpdir = name(kwargs['dir'])
        else:
            #If a string is given and it is a directory
            if isinstance(kwargs['dir'],str) and file.is_dir(kwargs['dir']):
                #Use that directory
                tmpdir = kwargs['dir']
            else:
                #If not, just create a temp dir
                tmpdir = name(dir())
    else:
        #Create a tempdir if none given
        tmpdir = name(dir())
    
    return tmpfile(f'{tmpdir}/{filename}')

