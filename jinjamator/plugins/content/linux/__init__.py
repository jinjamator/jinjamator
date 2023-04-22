import shlex
import subprocess
import re
import pkgutil

import linux.file
import linux.disk
import linux.systemctl
import linux.gluster
import linux.fs

def run (cmd,con=False, **kwargs):
    if con == False:
        return exec_local(cmd, **kwargs)
    else:
        con_type = type(con)
        if str(con_type) == "<class 'netmiko.linux.linux_ssh.LinuxSSH'>":
            return exec_ssh(cmd,con, **kwargs)
        else:
            log.error(f"Can't execute command via {type(con)} - Not yet implemented")
            return False

def exec_ssh(cmd,con, **kwargs):
    if isinstance(cmd,str):
        ret = ssh.run(cmd,connection=con, **kwargs)
    elif isinstance(cmd,list):
        ret = ssh.run_mlt(cmd,connection=con, **kwargs)
    else: ret = ""
    return [ret.strip("\n"),""]


def exec_local(cmd):
    cmd_list = shlex.split(cmd)
    ret = subprocess.run(cmd_list,capture_output=True)
    return [str(ret.stdout.decode("utf-8")).strip("\n"),str(ret.stderr.decode("utf-8")).strip("\n")]


def file_get (src,dst,con,**kwargs):
    con_type = type(con)
    if str(con_type) == "<class 'netmiko.linux.linux_ssh.LinuxSSH'>":
        ssh.get_file(src,dst,connection=con)
        return file.exists(dst)
        
    else:
        log.error(f"Can't execute command via {type(con)} - Not yet implemented")
        return False


def file_put (src,dst,con,**kwargs):
    con_type = type(con)
    if str(con_type) == "<class 'netmiko.linux.linux_ssh.LinuxSSH'>":
        if file.exists(src):
            ssh.put_file(src,dst,connection=con)
            return True
        else:
            return False
        
    else:
        log.error(f"Can't execute command via {type(con)} - Not yet implemented")
        return False


def mod_line_in_file (filename,regex,new_line,con,**kwargs):
    #file_o = run(f"cat {file}",con,**kwargs)
    match_first = False
    if "match_first" in kwargs:
        match_once = kwargs['match_first']
        del kwargs['match_first']

    file_o = read_file(filename,con,**kwargs)
    
    rgx = re.compile(regex)
    replaced = []
    newlines = []
    for line in file_o.splitlines():
        if not rgx.match(line) == None:
            replaced.append(line)
            newlines.append(new_line.strip("\n"))
            #Break if we only want to match the first
            if match_first: break
        else:
            newlines.append(line.strip("\n"))
    
    new_content = "\n".join(newlines)
    write_file(new_content,filename,con)
    
    #return all lines that were replaced
    return replaced
    


def read_file (filename,con=False,**kwargs):
    if con == False:
        if file.is_file(filename):
            return file.load(filename)
        return False
    else:
        con_type = type(con)
        if str(con_type) == "<class 'netmiko.linux.linux_ssh.LinuxSSH'>":
            tfilename = temp.file().name
            if file_get(filename,tfilename,con,**kwargs):
                return file.load(tfilename)
            else:
                return False
        else:
            log.error(f"Can't execute command via {type(con)} - Not yet implemented")
            return False


def write_file (content,filename,con,**kwargs):
    if con == False:
        if file.is_file(filename):
            return file.save(content,filename)
        return False
    else:
        con_type = type(con)
        if str(con_type) == "<class 'netmiko.linux.linux_ssh.LinuxSSH'>":
            tfilename = temp.file().name
            file.save(content,tfilename)

            if file_put(tfilename,filename,con,**kwargs):
                return True
            else:
                return False
        else:
            log.error(f"Can't execute command via {type(con)} - Not yet implemented")
            return False


