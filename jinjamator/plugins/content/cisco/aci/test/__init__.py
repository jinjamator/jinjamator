from dictdiffer import diff


class ACIObjectExists(ValueError):
    pass


class ACIObjectNotEqual(ValueError):
    pass


def create_verify(task_dir, config={}):
    py_load_plugins(globals())
    expected_data = json.loads(
        task.run(task_dir, config, output_plugin="null")[0]["result"]
    )

    expected_obj = expected_data["imdata"][0]
    expected_obj_type = list(expected_obj.keys())[0]
    expected_dn = expected_obj[expected_obj_type]["attributes"]["dn"]

    if cisco.aci.dn_exists(expected_dn):
        if _jinjamator.configuration.get("force_overwrite_existing_objects"):
            log.warning(
                "overwriting existing object {expected_dn} because force_overwrite_existing_objects is True."
            )
        else:
            raise ACIObjectExists(f"{expected_dn} exists, aborting test")

    configured_data = json.loads(
        task.run(task_dir, config, output_plugin="apic")[0]["result"]
    )

    configured_obj = configured_data["imdata"][0]
    configured_obj_type = list(configured_obj.keys())[0]
    configured_dn = configured_obj[configured_obj_type]["attributes"]["dn"]

    if configured_obj[configured_obj_type].get("children"):
        query_url = f"/api/mo/{configured_dn}.json?rsp-prop-include=config-only&rsp-subtree=full"
    else:
        query_url = f"/api/mo/{configured_dn}.json?rsp-prop-include=config-only"
    data = cisco.aci.query(query_url)["imdata"][0]

    res = list(diff(configured_obj, data))

    if not res:
        return "OK"
    else:
        return f"Data configured != data received {res}"


def delete_verify(task_dir, config={}):
    py_load_plugins(globals())

    config["undo"] = "yes"
    configured_data = json.loads(
        task.run(task_dir, config, output_plugin="apic")[0]["result"]
    )

    expected_data = json.loads(
        task.run(task_dir, config, output_plugin="null")[0]["result"]
    )
    expected_obj = expected_data["imdata"][0]
    expected_obj_type = list(expected_obj.keys())[0]
    expected_dn = expected_obj[expected_obj_type]["attributes"]["dn"]

    if not cisco.aci.dn_exists(expected_dn):
        return "OK"
    else:
        return f"{expected_dn} does exists after delete"
