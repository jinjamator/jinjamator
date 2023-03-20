#import jinjamator.plugins.content.ssh as ssh
#import jinjamator.plugins.content.linux as linux
#import jinjamator.plugins.content.json as json

def exists_native (path,con=False):
    out = linux.run(f"[[ -b {path} ]] && echo 1 || echo 0",con)
    if "1" in out[0]: return True
    else: return False


def lsblk (cmd,con=False,**kwargs):
    if 'data' in kwargs: return kwargs['data']
    out = linux.run(f"lsblk -J {cmd}",con,**kwargs)
    #print (out)
    if not "not a block device" in out[0]: return json.loads(out[0])
    else: return {}

def exists (path,con=False,**kwargs):
    q = lsblk(f"-p {path}",con,**kwargs)
    if 'blockdevices' in q: return True
    else: return False

def get_all (con=False,**kwargs):
    return lsblk("-O -p",con,**kwargs)['blockdevices']

def get (path,con=False,**kwargs):
    #Process data that was passed through
    if 'data' in kwargs: 
        for dat in kwargs['data']:
            if dat['name'] == path: return [dat]
        return []
    else:
        return lsblk(f"-O -p {path}",con,**kwargs)['blockdevices']

def is_mounted (path,con=False,**kwargs):
    q = get(path,con,**kwargs)
    if q[0]['mountpoint'] == 'None' or q[0]['mountpoint'] == None: return False
    else: return True

def has_fs (path,con=False,**kwargs):
    q = get(path,con,**kwargs)
    if q[0]['fstype'] == 'None' or q[0]['mountpoint'] == None: return False
    else: return True

