from textfsmplus import TextFSM
import os
from jinjamator.plugins.content import file
from jinjamator import plugin_loader
from io import StringIO


def parse(path):
    plugin_loader.content.py_load_plugins(globals())
    from os.path import dirname

    raw_data = file.load(path)
    base_path = dirname(__file__)

    fields = None
    for line in raw_data.split("\n"):
        if line.startswith("#Fields"):
            fields = line.replace("#Fields: ", "")
            break
    if not fields:
        raise ValueError(f"Cannot find field description in file {path}")
    fsm_mappings = []
    for field, mapping in yaml.loads(file.load(f"{base_path}/fsm/aclog.mapping.yaml"))[
        "fields"
    ].items():
        if isinstance(mapping["name"], str):
            name = str(mapping["name"])
            fields = fields.replace("%" + field, "${" + name + "}")
            if (f"Value Required {name} {mapping['regex']}") not in fsm_mappings:
                fsm_mappings.append(f"Value Required {name} {mapping['regex']}")

        elif isinstance(mapping["name"], list):
            replacement = ""
            for index, name in enumerate(mapping["name"]):
                if name:
                    replacement += "${" + str(name) + "}"
                    if (
                        f"Value Required {name} {mapping['regex'][index]}"
                    ) not in fsm_mappings:
                        fsm_mappings.append(
                            f"Value Required {name} {mapping['regex'][index]}"
                        )

                else:
                    replacement += str(mapping["regex"][index])
            fields = fields.replace("%" + field, replacement)
    if "%" in fields:
        raise NotImplementedError(f"Missing mapping for field. {fields}")

    dynamic_fsm_template = task.run(
        dirname(__file__) + "/fsm/aclog.textfsm.j2",
        {"MAPPINGS": "\n".join(fsm_mappings), "LINE_SPEC": fields},
        output_plugin="null",
    )[0]["result"]
    log.debug(dynamic_fsm_template)
    re_table = TextFSM(StringIO(dynamic_fsm_template))
    retval = []
    for row in re_table.ParseText(raw_data):
        tmp = {}
        for i, v in enumerate(re_table.header):
            tmp[v] = row[i]
        retval.append(tmp)
    return retval
