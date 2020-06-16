def is_possible(timeout=1):
    """ 
    Check if all vars for apic login are defined and make a test query to determine if the login works
    """
    from jinjamator.plugin_loader.content import py_load_plugins

    py_load_plugins(globals())
    if (
        "apic_url" in self._parent.configuration._data
        and "apic_username" in self._parent.configuration._data
        and "apic_password" in self._parent.configuration._data
    ) or (
        "apic_key" in self._parent.configuration._data
        and "apic_cert_name" in self._parent.configuration._data
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
