import socket


def get_service_name_by_proto_and_port(port, proto="tcp", numeric_only=False):
    try:
        if numeric_only:
            return "{0}-{1}".format(proto, port).upper()
        else:
            return "{0}-{1}".format(proto, socket.getservbyport(port, proto)).upper()
    except OSError:
        log.debug("service name not found using proto_port notation")
        return "{0}-{1}".format(proto, port).upper()
