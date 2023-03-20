

def status (con=False):
    out = linux.run("gluster peer status",con)
    return fsm.process('linux', 'gluster peer status' , data=out[0])

def probe (ip,con=False):
    out = linux.run(f"gluster peer probe {ip}",con)
    if "peer probe" in out[0]:
        parts = out[0].split(":")
        return parts[1].strip()

def detach (ip,con=False,**kwargs):
    if 'force' in kwargs: f = "force"
    else: f = ""
    cmds = [
        f"gluster peer detach {ip}{f}",
        "y"
    ]
    out = linux.run(cmds,con,last_read=1.0)
    for line in out[0].splitlines():
        if line.startswith('peer detach'):
            parts = line.split(":")
            return parts[1].strip()
    
    return False

