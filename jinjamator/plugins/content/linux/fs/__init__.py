# from jinjamator.plugins.content.linux.file import is_block
# import jinjamator.plugins.content.ssh as ssh
# import jinjamator.plugins.content.log as log
# import jinjamator.plugins.content.linux.disk as linux_disk
# import jinjamator.plugins.content.linux as linux


def create (path,fstype,con=False,**kwargs):
    if not 'force' in kwargs or ('force' in kwargs and kwargs['force'] == False):
        #fs_exist = linux.disk.has_fs(path,con,**kwargs)
        #Hack because JM bug
        fs_exist = linux_disk.has_fs(path,con,**kwargs)
        if 'force' in kwargs: del kwargs['force']
    else:
        #Force fs creation
        fs_exist = False
        del kwargs['force']
    
    if "fs_options" in kwargs: 
        fs_opt = kwargs['fs_options']
        del kwargs['fs_options']
    else: fs_opt = ""

    if fs_exist == False:
        return linux.run(f"mkfs -t {fstype} {fs_opt} {path}",con,**kwargs)[0]
    else: 
        log.error(f"Cannot create FS '{fstype}' on device {path} because it already has a filesystem and creation is not forced")
        return False


def mount_block (disk,mountpoint,con=False):
    if not linux.file.is_block(disk,con):
        log.error(f"Cannot create mountpoint, not a block device: {disk}")
        return False
    if not linux.file.is_dir(mountpoint,con):
        log.error(f"Cannot create mountpoint, not a directory: {mountpoint}")
        return False
    
    mpret = create_mountpoint(mountpoint,con)
    if not linux.file.is_dir(mountpoint,con):
        log.error(f"Created mountpoint, but it is not here: {mountpoint}")
        log.error(f"Got: {mpret}")
        return False
    
    #Do mount
    mnt = linux.fs.xfs.dab()



def create_mountpoint (path,con=False):
    return linux.file.mkdir(path,con)
