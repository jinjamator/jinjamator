import logging
from jinjamator.plugins.content.file import load
import os

log = logging.getLogger()


def site_path():
    return _jinjamator._configuration.get("jinjamator_site_path", None)


def jinjamator_base_directory():
    return _jinjamator._configuration.get("jinjamator_base_directory", None)


def jinjamator_global_tasks_base_dirs():
    return _jinjamator._configuration.get("global_tasks_base_dirs", None)


def python_requirements():
    return load(os.path.join(jinjamator_base_directory(), "requirements.txt")).split(
        "\n"
    )
