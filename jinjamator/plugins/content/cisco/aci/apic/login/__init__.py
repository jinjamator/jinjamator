def _get_missing_apic_connection_vars():
    inject = []
    if not _jinjamator.configuration["apic_url"]:
        inject.append("apic_url")
    if not _jinjamator.configuration["apic_username"]:
        inject.append("apic_username")
    if not cisco.aci.credentials_set():
        inject.append("apic_password")
    return inject



def is_possible(timeout=1,*, _requires=_get_missing_apic_connection_vars):
    """ 
    Check if all vars for apic login are defined and make a test query to determine if the login works
    """



    try:
        sess = cisco.aci.connect_apic()
        res=not sess.login_error
        sess.close()
        return res
    except Exception as e:
        log.error(e)
        return not sess.login_error
    return False

    
    
