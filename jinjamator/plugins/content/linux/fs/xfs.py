#import jinjamator.plugins.content.ssh as ssh
#import jinjamator.plugins.content.log as log
import jinjamator.plugins.content.linux.fs as linux_fs

def is_valid_fs (string):
    if "is not a valid XFS filesystem" in string: return False
    else: return True


def get_label (path,con=False,**kwargs):
    if 'force' in kwargs: del kwargs['force']
    if 'fs_options' in kwargs: del kwargs['fs_options']

    q = xfs_admin(f"-l {path}",con,**kwargs)
    if q:
        q2 = q.replace("label = ","")
        return q2.replace('"','')
    else: 
        log.error(f"{path} is not a valid XFS filesystem")
        return False

def set_label (path,label,con=False,**kwargs):
    if 'force' in kwargs: del kwargs['force']
    if 'fs_options' in kwargs: del kwargs['fs_options']

    q = xfs_admin(f"-L {label} {path}",con,**kwargs)
    if "new label =" in q: return True
    else: return False


def xfs_admin (args,con=False,**kwargs):
    out = linux.run(f"xfs_admin {args}",con,**kwargs)[0]
    if is_valid_fs(out): return out
    else: return False

def create (path,con=False,**kwargs):
    if 'force' in kwargs and kwargs['force'] == True:
        if 'fs_options' in kwargs: kwargs['fs_options'] += " -f"
        else: kwargs['fs_options'] = "-f"
    #return linux.fs.create(path,"xfs",con,**kwargs)
    #Hack because JM bug
    create = linux_fs.create(path,"xfs",con,**kwargs)
    if create == False:
        return create
    else:
        if isinstance(get_label(path,con,**kwargs),str): return True
        else: return False

def dab():
    print("dab")