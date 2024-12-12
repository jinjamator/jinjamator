# as a jinjamator python tasklet is pure python you can always import any external
# lib or function 
from pprint import pformat
from datetime import datetime

return_value = []
ts=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# lets manipulate the generated excel_file_name defined in the defaults by adding a timestamp
self.configuration['excel_file_name']=f"{self.configuration['excel_file_name']}_{ts}"

# device_list is defined in defaults.yaml. All data defined in
# defaults.yaml will automatically be injected,
# if not defined via -m on CLI or in a site configuration (deamon mode)
for hostname in device_list:    
    try:
        # as ssh_host is variable we define it via a kwarg, so
        # jinjamator dependency injection just asks for ssh_username
        # and ssh_password if not defined in a site or via -m commandline
        # mapping. Also lower netmiko connection timeout to 1s 
        result = cisco.ios.query("show inventory", ssh_host=hostname, conn_timeout=1)
        for line in result:
            line["hostname"] = hostname
            log.debug(f"got row: {pformat(line)}")
    except Exception as e:
        log.warning(e)
        result=None
    if result:
        return_value += result
# just return the data generated
return return_value
