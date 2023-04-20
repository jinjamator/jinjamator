import pathlib

def exists (path,con=False):
    return check_file(path,"-e",con)

def is_file (path,con=False):
    return check_file(path,"-f",con)

def is_dir (path,con=False):
    return check_file(path,"-d",con)

def is_block (path,con=False):
    return check_file(path,"-b",con)

def is_symlink (path,con=False):
    return check_file(path,"-L",con)

def is_socket (path,con=False):
    return check_file(path,"-S",con)

def is_writeable (path,con=False):
    return check_file(path,"-w",con)

def is_exec (path,con=False):
    return check_file(path,"-x",con)

def is_not_empty (path,con=False):
    return check_file(path,"-s",con)



def check_file (path,operator,con=False):
    if con == False: return check_file_local(path,operator)
    out = linux.run(f"[[ {operator} {path} ]] && echo 1 || echo 0",con)
    if "1" in out[0]: return True
    else: return False


def check_file_local (path,operator):
    if operator == "-e": return pathlib.Path(path).exists()
    elif operator == "-f": return pathlib.Path(path).is_file()
    elif operator == "-d": return pathlib.Path(path).is_dir()
    elif operator == "-b": return pathlib.Path(path).is_block_device()
    elif operator == "-L": return pathlib.Path(path).is_symlink()
    elif operator == "-S": return pathlib.Path(path).is_socket()
    else:
        log.error(f"Operator {operator} is not supported for local")
        return None


def mkdir (path,con=False):
    if con == False: return file.mkdir_p(path)

    return linux.run(f"mkdir -p {path}",con)[0]