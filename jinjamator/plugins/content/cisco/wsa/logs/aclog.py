from textfsm import TextFSM
import os
from jinjamator.plugins.content import file


def parse(path):
    raw_data = file.load(path)
    base_path = os.path.dirname(__file__)
    template = f"{base_path}/fsm/aclog.textfsm"
    re_table = TextFSM(file.open(template))
    retval = []
    for row in re_table.ParseText(raw_data):
        tmp = {}
        for i, v in enumerate(re_table.header):
            tmp[v] = row[i]
        retval.append(tmp)
    return retval
