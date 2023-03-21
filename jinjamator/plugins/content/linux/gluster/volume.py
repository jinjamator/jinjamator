#volume add-brick <VOLNAME> [<replica> <COUNT> [arbiter <COUNT>]] <NEW-BRICK> ... [force] - add brick to volume <VOLNAME>
#volume barrier <VOLNAME> {enable|disable} - Barrier/unbarrier file operations on a volume
#volume clear-locks <VOLNAME> <path> kind {blocked|granted|all}{inode [range]|entry [basename]|posix [range]} - Clear locks held on path
#volume create <NEW-VOLNAME> [[replica <COUNT> [arbiter <COUNT>]]|[replica 2 thin-arbiter 1]] [disperse [<COUNT>]] [disperse-data <COUNT>] [redundancy <COUNT>] [transport <tcp|rdma|tcp,rdma>] <NEW-BRICK> <TA-BRICK>... [force] - create a new volume of specified type with mentioned bricks
#volume delete <VOLNAME> - delete volume specified by <VOLNAME>
#volume geo-replication [<PRIMARY-VOLNAME>] [<SECONDARY-IP>]::[<SECONDARY-VOLNAME>] {\
# create [[ssh-port n] [[no-verify] \
# | [push-pem]]] [force] \
# | start [force] \
# | stop [force] \
# | pause [force] \
# | resume [force] \
# | config [[[\!]<option>] [<value>]] \
# | status [detail] \
# | delete [reset-sync-time]}  - Geo-sync operations
#volume get <VOLNAME|all> <key|all> - Get the value of the all options or given option for volume <VOLNAME> or all option. gluster volume get all all is to get all global options
#volume heal <VOLNAME> [enable | disable | full |statistics [heal-count [replica <HOSTNAME:BRICKNAME>]] |info [summary | split-brain] |split-brain {bigger-file <FILE> | latest-mtime <FILE> |source-brick <HOSTNAME:BRICKNAME> [<FILE>]} |granular-entry-heal {enable | disable}] - self-heal commands on volume specified by <VOLNAME>
#volume help - display help for volume commands
#volume info [all|<VOLNAME>] - list information of all volumes
#volume list - list all volumes in cluster
#volume log <VOLNAME> rotate [BRICK] - rotate the log file for corresponding volume/brick
#volume profile <VOLNAME> {start|info [peek|incremental [peek]|cumulative|clear]|stop} [nfs] - volume profile operations
#volume rebalance <VOLNAME> {{fix-layout start} | {start [force]|stop|status}} - rebalance operations
#volume remove-brick <VOLNAME> [replica <COUNT>] <BRICK> ... <start|stop|status|commit|force> - remove brick from volume <VOLNAME>
#volume replace-brick <VOLNAME> <SOURCE-BRICK> <NEW-BRICK> {commit force} - replace-brick operations
#volume reset <VOLNAME> [option] [force] - reset all the reconfigured options
#volume reset-brick <VOLNAME> <SOURCE-BRICK> {{start} | {<NEW-BRICK> commit}} - reset-brick operations
#volume set <VOLNAME> <KEY> <VALUE> - set options for volume <VOLNAME>
#volume set <VOLNAME> group <GROUP> - This option can be used for setting multiple pre-defined volume options where group_name is a file under /var/lib/glusterd/groups containing one key value pair per line
#volume start <VOLNAME> [force] - start volume specified by <VOLNAME>
#volume statedump <VOLNAME> [[nfs|quotad] [all|mem|iobuf|callpool|priv|fd|inode|history]... | [client <hostname:process-id>]] - perform statedump on bricks
#volume status [all | <VOLNAME> [nfs|shd|<BRICK>|quotad]] [detail|clients|mem|inode|fd|callpool|tasks|client-list] - display status of all or specified volume(s)/brick
#volume stop <VOLNAME> [force] - stop volume specified by <VOLNAME>
#volume sync <HOSTNAME> [all|<VOLNAME>] - sync the volume information from a peer
#volume top <VOLNAME> {open|read|write|opendir|readdir|clear} [nfs|brick <brick>] [list-cnt <value>] | {read-perf|write-perf} [bs <size> count <count>] [brick <brick>] [list-cnt <value>] - volume top operations


def create (volname,bricks,hosts,con=False,**kwargs):
    #volume create <NEW-VOLNAME> [[replica <COUNT> [arbiter <COUNT>]]|[replica 2 thin-arbiter 1]] 
    #[disperse [<COUNT>]] [disperse-data <COUNT>] [redundancy <COUNT>] [transport <tcp|rdma|tcp,rdma>] 
    #<NEW-BRICK> <TA-BRICK>... [force] - create a new volume of specified type with mentioned bricks
    args = [volname]
    log.info("Creating volume {volname}")
       
    #do set up depending on type
    #replica volume
    if 'replica' in kwargs:
        args.append(f"replica {str(kwargs['replica'])}")
        
        #Handle arbiter
        if 'arbiter' in kwargs: args.append(f"arbiter {str(kwargs['arbiter'])}")
        #Handle thin-arbiter and ignore the value set there (it's always 1)
        elif 'thin-arbiter' in kwargs and str(kwargs['replica']) == "2": args.append(f"thin-arbiter 1")
    #dispersed volume
    elif 'disperse' in kwargs:
        args.append(f"disperse {str(kwargs['disperse'])}")
        if 'redundancy' in kwargs: args.append(f"redundancy {str(kwargs['redundancy'])}")


    #set transport
    if 'transport' in kwargs and kwargs['transport'] in ["tcp","rdma","tcp,rdma"]: args.append(f"transport {kwargs['transport']}")
        
    #make a brick-list
    #if bricks is a string, ignore hosts and take only the brick-string
    if isinstance(bricks,str): args.append(bricks)
    else:
        args.append(host_brick_list(hosts,bricks))
    
    if 'force' in kwargs: args.append("force")

    cmdline = " ".join(args)
    log.debug(f"Compiled args: {cmdline}")
    out = linux.run(f"gluster volume create {cmdline}",con)
    
    return out[0]


def start (volname,con=False,**kwargs):
    if 'force' in kwargs: force = "force"
    else: force = ""

    out = linux.run(f"gluster volume start {volname} {force}",con)
    
    return out[0]


def host_brick_list (hosts,bricks):
    #Compiles a string which lists all given bricks over all hosts
    if not isinstance(hosts,list): log.error(f"Cannot create host-brick-list. Hosts is not a list ({type(hosts)}): {str(hosts)}")
    if not isinstance(bricks,list): log.error(f"Cannot create host-brick-list. Bricks is not a list ({type(bricks)}): {str(bricks)}")
    
    blist = []
    for brick in bricks:
        for host in hosts:
            blist.append(f"{host}:{brick}")
    
    return " ".join(blist)




#fake function
def status (con=False):
    out = linux.run("gluster peer status",con)
    return fsm.process('linux', 'gluster peer status' , data=out[0])