def is_possible(timeout=1):
    """ 
    Check if all vars for apic login are defined and make a test query to determine if the login works
    """
    from jinjamator.plugin_loader.content import py_load_plugins

    py_load_plugins(globals())
    if (
        "apic_url" in _jinjamator.configuration._data
        and "apic_username" in _jinjamator.configuration._data
        and "apic_password" in _jinjamator.configuration._data
    ) or (
        "apic_key" in _jinjamator.configuration._data
        and "apic_cert_name" in _jinjamator.configuration._data
    ):

        import logging

        log = logging.getLogger()

        try:
            sess = cisco.aci.connect_apic()
            sess.get("/api/aaaLogin.json", 1)
            sess.close()
        except Exception as e:
            sess.close()
            log.error(e)
            return False

        return True
    return False
