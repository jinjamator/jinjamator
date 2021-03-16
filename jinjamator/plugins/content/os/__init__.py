import os


def path():
    return os.path


def mkdir(path):
    os.makedirs(path, exist_ok=True)
