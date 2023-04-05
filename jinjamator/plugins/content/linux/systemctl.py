# import jinjamator.plugins.content.ssh as ssh


def status (service,con=False):
    ret = linux.run(f"systemctl status {service}",con)
    return fsm.process('linux', 'systemctl status' , data=ret[0])[0]

def start (service,con=False):
    return linux.run(f"systemctl start {service}",con)

def stop (service,con=False):
    return linux.run(f"systemctl stop {service}",con)

def enable (service,con=False):
    return linux.run(f"systemctl enable {service}",con)

def disable (service,con=False):
    return linux.run(f"systemctl disable {service}",con)

