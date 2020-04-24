import logging

log = logging.getLogger()


def site_path():
    log.debug(self._parent._configuration._data)

    return self._parent._configuration.get("jinjamator_site_path", None)
