from deepdiff import DeepDiff


class ACIObjectExists(ValueError):
    pass


class ACIObjectDoesNotExists(ValueError):
    pass


class ACIObjectNotEqual(ValueError):
    pass


class ACITooManyObjects(ValueError):
    pass


def create_verify(task_dir, config={}, ignore_fields=[]):
    py_load_plugins(globals())
    log.debug("")
    log.debug("######################################################################")
    log.debug("#  Running create_verify")
    log.debug("######################################################################")
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

    d_query_result = cisco.aci.query(query_url)
    if len(d_query_result["imdata"]) == 1:
        data = d_query_result["imdata"][0]
    elif len(d_query_result["imdata"]) == 0:
        raise ACIObjectDoesNotExists(
            f"Object which should exists does not exist dn {configured_dn}"
        )
    else:
        raise ACITooManyObjects(f"APIC returned too many Objects {data}")

    # Function to ignore fields that shall not be checked
    def exclude_obj_callback(obj, path):
        return True if path in ignore_fields else False

    # For some checks the order of items is somewhat unpredictable when reading from APIC (especially for unordered children)
    if _jinjamator.configuration.get("verify_ignore_order"):
        ddiff = DeepDiff(
            configured_obj,
            data,
            ignore_order=True,
            exclude_obj_callback=exclude_obj_callback,
        )
    else:
        ddiff = DeepDiff(
            configured_obj, data, exclude_obj_callback=exclude_obj_callback
        )

    if not ddiff:
        log.debug("*************** Verification OK ***************")
        return "OK"
    else:
        log.debug(
            "*************** Verification NOK ***************\n"
            + "Live data:\n"
            + json.dumps(data)
            + "\n\n"
        )

        raise ACIObjectNotEqual(
            f"Data configured != data received \n{json.dumps(json.loads(ddiff.to_json()))}"
        )


def delete_verify(task_dir, config={}):
    py_load_plugins(globals())
    log.debug("")
    log.debug("######################################################################")
    log.debug("#  Running delete_verify")
    log.debug("######################################################################")

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

    config["undo"] = False

    if not cisco.aci.dn_exists(expected_dn):
        log.debug("*************** Deletion OK ***************")
        return "OK"
    else:
        log.debug("*************** Deletion NOK ***************")
        log.debug(f"{expected_dn} does exists after delete")
        raise ACIObjectExists(f"{expected_dn} does exists after delete")


def verify_ignore_order(state=True):
    """
    Instruct the verify-process to ignore the order of json attributes

    :param state: Set to True or False
    :type state: boolean
    :returns: None
    :rtype: None
    """
    _jinjamator.configuration["verify_ignore_order"] = state
