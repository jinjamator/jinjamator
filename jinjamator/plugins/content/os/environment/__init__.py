import os


def get(var, default=None):
    """
    jinja2 helper function to access the os environment
    """

    return os.environ.get(var, default)


def pop(var, default=None):
    """
    jinja2 helper function to access the os environment
    """
    try:
        data = os.environ.pop(var)
    except KeyError:
        data = default
    return data
