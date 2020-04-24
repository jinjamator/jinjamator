def is_possible():
    """ 
    Check if all vars for apic login are defined.
    """
    if ("apic_url" in self._parent.configuration._data and "apic_username" in self._parent.configuration._data and "apic_password" in self._parent.configuration._data) or ("apic_key" in self._parent.configuration._data and "apic_cert_name" in self._parent.configuration._data):
        return True
    return False
