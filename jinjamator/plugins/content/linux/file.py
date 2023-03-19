import jinjamator.plugins.content.linux as linux


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
    if operator == "-e": return file.exists(path)
    elif operator == "-f": return file.is_file(path)
    elif operator == "-d": return file.is_dir(path)
    elif operator == "-b": return file.is_block(path)
    elif operator == "-L": return file.is_symlink(path)
    elif operator == "-S": return file.is_socket(path)
    else:
        log.error(f"Operator {operator} is not supported for local")
        return None


def mkdir (path,con=False):
    if con == False: return file.mkdir_p(path)

    return linux.run(f"mkdir -p {path}",con)[0]