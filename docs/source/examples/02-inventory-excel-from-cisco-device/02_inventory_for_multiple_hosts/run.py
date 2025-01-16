# just return the data generated by cisco.ios.query, as this uses dependency
# injection, jinjamator will automatically ask for required inputs
return_value = []
# device_list is defined in defaults.yaml. All data defined in
# defaults.yaml will automatically be injected,
# if not defined via -m on CLI or in a site configuration (deamon mode)
for hostname in device_list:
    # as ssh_host is variable we define it via a kwarg, so
    # jinjamator dependency injection just asks for ssh_username
    # and ssh_password if not defined in a site or via -m commandline
    # mapping
    result = cisco.ios.query("show inventory", ssh_host=hostname)
    for line in result:
        line["hostname"] = hostname
    return_value += result
return return_value