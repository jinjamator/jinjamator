import logging

log = logging.getLogger()


def site_path():
    return self._parent._configuration.get("jinjamator_site_path", None)
