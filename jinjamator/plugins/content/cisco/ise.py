# this is just a helper plugin to make pyise-ers module available as plugin

def _get_missing_ise_connection_vars():
    inject = []
    for required_var in ['ise_hostname', 'ise_username', 'ise_password' ]:
        if required_var not in _jinjamator.configuration._data:
            inject.append(required_var)
    return inject
    
def connect(verify=False,disable_warnings=True, *,_requires=_get_missing_ise_connection_vars):
    try:
        from pyiseers import ERS
    except:
        log.error('module pyiseers not available install via pip/pipx install pyise-ers')
        return None
    return ERS(ise_node=_jinjamator.configuration._data.get('ise_hostname'), ers_user=_jinjamator.configuration._data.get('ise_username'), ers_pass=_jinjamator.configuration._data.get('ise_password'), verify=verify, disable_warnings=disable_warnings)