import os
import logging

log = logging.getLogger(__name__)


def save(data, target, **kwargs):
    """
    save data to file
    """
    mode = kwargs.get("mode", "w")
    if (not os.path.exists(target)) or (
        kwargs.get("overwrite", True) and os.path.isfile(target)
    ):
        with open(target, mode=mode) as fh:
            fh.write(data)
        return True
    log.error(f"Path {target} exists and overwrite is not true or path is a directory")
    return False
