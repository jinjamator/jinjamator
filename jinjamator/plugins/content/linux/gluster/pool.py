def list (con=False):
    out = linux.run("gluster pool list",con)
    return fsm.process('linux', 'gluster pool list' , data=out[0])