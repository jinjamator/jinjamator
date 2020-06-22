from deepdiff import DeepDiff


class ACIObjectExists(ValueError):
    pass


class ACIObjectDoesNotExists(ValueError):
    pass


class ACIObjectNotEqual(ValueError):
    pass


class ACITooManyObjects(ValueError):
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
        query_url = f"/api/mo/{configured_dn}.json?rsp-prop-include=config-only&rsp-subtree=children"
    else:
        query_url = f"/api/mo/{configured_dn}.json?rsp-prop-include=config-only"

    d_query_result = cisco.aci.query(query_url)
    if len(d_query_result["imdata"]) == 1:
        data = d_query_result["imdata"][0]
    elif len(d_query_result["imdata"]) == 0:
        raise ACIObjectDoesNotExists(
            f"Object which should exists does not exist dn {configured_dn}"
        )
    else:
        raise ACITooManyObjects(f"APIC returned too many Objects {data}")

    ddiff = DeepDiff(configured_obj, data)

    if not ddiff:
        return "OK"
    else:

        raise ACIObjectNotEqual(
            f"Data configured != data received \n{json.dumps(json.loads(ddiff.to_json()))}"
        )


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
        return ACIObjectExists(f"{expected_dn} does exists after delete")
