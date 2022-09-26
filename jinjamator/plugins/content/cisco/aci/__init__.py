# Copyright 2019 Wilhelm Putz

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import jinja2
from jinjamator.external.acitoolkit.acisession import Session
import json

import re
import logging
import getpass

# from jinjamator.tools.aciwatcherthread import ACIWatcherThread
from pprint import pprint

log = logging.getLogger()


switchdb = {
    "N9K-C93108TC-EX": {
        "uplinks": [49, 50, 51, 52, 53, 54],
        "downlinks": range(1, 49),
        "type": "leaf",
    },
    "N9K-C93108TC-FX": {
        "uplinks": [49, 50, 51, 52, 53, 54],
        "downlinks": range(1, 49),
        "type": "leaf",
    },
    "N9K-C93180YC-FX": {
        "uplinks": [49, 50, 51, 52, 53, 54],
        "downlinks": range(1, 49),
        "type": "leaf",
    },
    "N9K-C93240YC-FX2": {
        "uplinks": [49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60],
        "downlinks": range(1, 49),
        "type": "leaf",
    },
    "N9K-C9348GC-FXP": {"uplinks": [53, 54], "downlinks": range(1, 53), "type": "leaf"},
    "N9K-C93180YC-EX": {
        "uplinks": [49, 50, 51, 52, 53, 54],
        "downlinks": range(1, 49),
        "type": "leaf",
    },
    "N2K-B22HP-P": {"uplinks": range(17, 25), "downlinks": range(1, 17), "type": "fex"},
    "N2K-C2248TP-1GE": {
        "uplinks": range(49, 53),
        "downlinks": range(1, 49),
        "type": "fex",
    },
    "N9K-C9364C": {"uplinks": [], "downlinks": range(1, 67), "type": "spine"},
    "N9K-C9332C": {"uplinks": [], "downlinks": range(1, 35), "type": "spine"},
    "N9K-C9336PQ": {"uplinks": [], "downlinks": range(1, 37), "type": "spine"},
    "N9K-C93216TC-FX2": {
        "uplinks": range(96, 109),
        "downlinks": range(1, 97),
        "type": "leaf",
    },
    "N9K-C9396PX": {
        "uplinks": range(49, 61),
        "downlinks": range(1, 49),
        "type": "leaf",
    },
    "TEST-LEAF": {"uplinks": range(49, 50), "downlinks": range(1, 2), "type": "leaf"},
    "TEST-SPINE": {"uplinks": [], "downlinks": range(1, 2), "type": "spine"},
    "TEST-FEX": {"uplinks": range(49, 50), "downlinks": range(1, 2), "type": "fex"},
}

log = logging.getLogger()


def credentials_set():
    """
    Check if jinjamator has all information set necessary to connect to APIC.

    :returns: True if all required APIC connection parameters are set, False if not.
    :rtype: boolean
    """
    if (
        "apic_username" in _jinjamator.configuration.keys()
        and "apic_key" in _jinjamator.configuration.keys()
        and "apic_cert_name" in _jinjamator.configuration.keys()
    ) or (
        "apic_username" in _jinjamator.configuration.keys()
        and "apic_password" in _jinjamator.configuration.keys()
    ):
        return True
    # _jinjamator._log.info(_jinjamator.configuration.keys())
    return False


def _get_missing_apic_connection_vars():
    inject = []
    if not _jinjamator.configuration["apic_url"]:
        inject.append("apic_url")
    if not _jinjamator.configuration["apic_username"]:
        inject.append("apic_username")
    if not credentials_set():
        inject.append("apic_password")
    return inject


def connect_apic(
    subscription_enabled=False, *, _requires=_get_missing_apic_connection_vars
):
    if not _jinjamator.configuration["apic_key"]:
        del _jinjamator.configuration["apic_key"]
    if not _jinjamator.configuration["apic_cert_name"]:
        del _jinjamator.configuration["apic_cert_name"]
    if (
        "apic_key" in _jinjamator.configuration.keys()
        and "apic_cert_name" in _jinjamator.configuration.keys()
    ):
        apic_session = Session(
            _jinjamator.configuration["apic_url"],
            _jinjamator.configuration["apic_username"],
            cert_name=_jinjamator.configuration["apic_cert_name"],
            key=_jinjamator.configuration["apic_key"],
            subscription_enabled=False,
        )
    else:
        if not _jinjamator.configuration["apic_password"]:
            _jinjamator.handle_undefined_var("apic_password")
        apic_session = Session(
            _jinjamator.configuration["apic_url"],
            _jinjamator.configuration["apic_username"],
            _jinjamator.configuration["apic_password"],
            subscription_enabled=subscription_enabled,
        )
        apic_session.login()
    return apic_session


def query(query_url, timeout=60, *, _requires=_get_missing_apic_connection_vars):
    """[summary]

    :param query_url: URL for the query, eg. "/api/node/class/topology/pod-1/node-101/faultSummary.json". \
If the URL contains "subscription=yes as parameter", a websocket session will be opened automatically.
    :type query_url: ``str``
    :param timeout: Timeout waiting for an http response from the apic, defaults to 60
    :type timeout: int, optional
    :return: dictionary containing the response from the APIC
    :rtype: ``dict``
    """

    if not query_url.startswith("/"):
        query_url = f"/{query_url}"
    if "subscription=yes" in query_url:
        subscription_enabled = True
    else:
        subscription_enabled = False
    session = connect_apic(subscription_enabled)
    try:
        data = session.get(query_url, timeout)
    except Exception as e:
        log.error(e)
        session.close()
        return {"imdata": [], "totalCount": "0"}
    session.close()
    return json.loads(data.text)


def model_is_spine(model):
    if model in [
        "N9K-C9336PQ",
        "N9K-C9364C",
        "N9K-C9332C",
        "N9K-C9504",
        "N9K-C9508",
        "N9K-C9516",
        "N9K-C9332C",
    ]:
        return True
    return False


def get_leaf_types():
    return [switch for switch in switchdb.keys() if switchdb[switch]["type"] == "leaf"]


def get_spine_types():
    return [switch for switch in switchdb.keys() if switchdb[switch]["type"] == "spine"]


def get_fex_types():
    return [switch for switch in switchdb.keys() if switchdb[switch]["type"] == "fex"]


def model_is_leaf(model):
    if model.beginswith("APIC"):
        return False
    return not aci_model_is_spine(model)


def get_role_by_model(model):
    if aci_model_is_spine(model):
        return "spine"
    elif aci_model_is_leaf(model):
        return "leaf"
    elif model.beginswith("APIC"):
        return "controller"
    else:
        return "unspecified"


def get_all_uplinks(model):
    return switchdb[model.upper()]["uplinks"]


def get_convertible_uplinks(model, count, min_uplinks=2):
    try:
        possible = switchdb[model]["uplinks"][-count:]
    except KeyError:
        return []
    if len(switchdb[model]["uplinks"]) - len(possible) < min_uplinks:
        return []
    return possible


def get_all_downlinks(model):
    """
    Return all downlink ports from plugin internal switch database.

    :param model: Cisco Switch Model String
    :type model: string
    :returns: A list of all default downlink port numbers.
    :rtype: list
    """
    try:
        return switchdb[model.upper()]["downlinks"]
    except KeyError:
        raise ValueError(f"Switchmodel {model} is not supported")


def get_parent_dn_from_child_dn(dn):
    dn = re.sub(r"\[\S+\]", "", dn)
    tmp = dn.split("/")
    return "/".join(tmp[:-1])


def is_dn_in_use(
    dn, ignore_children=False, *, _requires=_get_missing_apic_connection_vars
):
    in_use = False
    retval = query("/api/node/mo/{0}.json?query-target=children".format(dn))
    log.debug(retval)
    if int(retval["totalCount"]) != len(retval["imdata"]):
        log.warning(
            "ACI API bug detected -> totalCount is {0} but {1} objects retured -> fixing up".format(
                retval["totalCount"], len(retval["imdata"])
            )
        )
        retval["totalCount"] = str(len(retval["imdata"]))

    if int(retval["totalCount"]) > 0 and not ignore_children:
        log.info("dn has child objects -> is in use")
        in_use = True
    elif int(retval["totalCount"]) > 0 and type(ignore_children) == list:
        for i in ignore_children:
            log.info("dn has child objects -> ignoring {0} by user request".format(i))
            for x, child in enumerate(retval["imdata"]):
                if list(child.keys())[0] == i:
                    del retval["imdata"][x]
        if len(retval["imdata"]) > 0:
            log.info("dn has child objects -> is in use")
            in_use = True
    retval = query(
        "/api/node/mo/{0}.json?query-target=children&target-subtree-class=relnFrom".format(
            dn
        )
    )
    log.debug(retval)
    in_use_count = 0
    if int(retval["totalCount"]) > 0:
        for obj in retval["imdata"]:
            in_use_count += 1
            try:
                obj_type = list(obj.keys())[0]
                if obj[obj_type]["attributes"]["childAction"] in ["deleteNonPresent"]:
                    log.info(
                        "ignoring {0} with childAction deleteNonPresent relation".format(
                            obj_type
                        )
                    )
                    in_use_count -= 1
            except KeyError:
                pass

    if in_use_count > 0:
        log.info("object has active relnFrom objects -> is in use")
        in_use = True
    return in_use


def dn_exists(dn, *, _requires=_get_missing_apic_connection_vars):
    """
    Checks if the dn exists. Logs API Error to error log.

    :param dn: APIC dn-string
    :type dn: ``str``
    :returns: True if dn exists (or contains an error), false if not existing
    :rtype: ``bool``
    """
    data = query("/api/node/mo/{0}.json".format(dn))
    if len(data["imdata"]) > 0:
        if "error" in data["imdata"][0]:
            log.error(parse_api_error(data))
        return True
    return False


def parse_api_error(response):
    """
    Parse the error-message from the API Response.
    Assumes, that a check if there is an error present was done beforehand.

    :param response: Dict of the request response ([imdata][0][....])
    :type response: ``dict``
    :returns: Parsed Error-Text
    :rtype: ``str``
    """
    if "error" in response["imdata"][0]:
        return (
            "API-Errorcode "
            + str(response["imdata"][0]["error"]["attributes"]["code"])
            + ": "
            + str(response["imdata"][0]["error"]["attributes"]["text"])
        )
    else:
        return "Unparseable: " + str(response)


def is_api_error(response):
    """
    Check the API-Response for errors

    :param response: Dict of the request response ([imdata][0][....])
    :type response: ``dict``
    :returns: True if response contains an error, false if not
    :rtype: ``bool``
    """
    try:
        if "error" in response["imdata"][0]:
            return True
        else:
            return False
    except IndexError:
        log.debug("got empty response from APIC -> this is not an error")
        return False


def get_podid_by_switch_id(switch_id, *, _requires=_get_missing_apic_connection_vars):
    """
    Retrive the pod_id for a switch_id from APIC, if not possible ask user to enter pod_id

    :param switch_id: integer from 100 to 3999
    :type switch_id: ``int``
    :returns: pod_id
    :rtype: ``int``
    :raises ValueError: If the node with the specified apic_node_id is invalid.
    """
    if int(switch_id) > 99 and int(switch_id) < 4000:
        pass
    else:
        raise ValueError("Valid switch id must be between 99 and 4000")

    data = query(
        f'/api/node/class/fabricNode.json?query-target-filter=and(eq(fabricNode.id,"{switch_id}"))'
    )
    if is_api_error(data) or len(data["imdata"]) == 0:
        var_name = f"{switch_id}_pod_id"
        if _jinjamator.configuration.get(var_name):
            return _jinjamator.configuration.get(var_name)
        _jinjamator.handle_undefined_var(var_name)
        return _jinjamator.configuration.get(var_name)
    return (
        get_parent_dn_from_child_dn(data["imdata"][0]["fabricNode"]["attributes"]["dn"])
        .split("/")[-1:][0]
        .split("-")[1]
    )


def version(apic_node_id=1, *, _requires=_get_missing_apic_connection_vars):
    """
    Returns the firmware version of an APIC

    :param apic_node_id: Node id of the apic to query for the version from 1 to 10, defaults to 1
    :type apic_node_id: integer, optional
    :returns: Version information as returned from APIC e.g.: 4.2(1p)
    :rtype: string
    :raises ValueError: If the node with the specified apic_node_id cannot be found.

    """
    result = query(
        f'/api/node/class/firmwareCtrlrRunning.json?query-target-filter=and(wcard(firmwareCtrlrRunning.dn,"node-{apic_node_id}"))'
    )
    try:
        return result["imdata"][0]["firmwareCtrlrRunning"]["attributes"]["version"]
    except KeyError:
        raise ValueError("Node {apic_node_id} does not exist or is not an APIC")


def is_min_version(major, minor, patch_level=None, node_id=1):
    """Checks if the APIC run a minimum version specified

    :param major: minimum APIC major version, eg.: 4 for ACI 4.x.x
    :type major: ``int``
    :param minor: minimum APIC major version, eg.: 2 for ACI x.2.x
    :type minor: ``int``
    :param patch_level: minimum APIC patchlevel . eg.: 4i for ACI x.x.(4i) or None if it should be ignored
    :type patch_level: ``str`` or ``None``
    :param node_id: APIC node id to query, defaults to 1
    :type node_id: ``int``, optional
    :return: True if the APIC run specified version or greater, False if not.
    :rtype: ``bool``

    :Examples:

        jinja2 tasklet:

            .. code-block:: jinja

                {% if aci_is_min_version(4, 2, None) %} {#check if APIC runs at least 4.2 version of code#}
                bla bla
                {% endif %}

        python tasklet:

            .. code-block:: python

                if aci_is_min_version(4, 2, None): //check if APIC runs at least 4.2 version of code
                    do_something_fancy()
                else:
                    do_other_things()


    """

    #
    #

    running_version = version(node_id)
    m = re.match(
        r"(?P<major>\d+)\.(?P<minor>\d+)\((?P<patchlevel>.+)\)", running_version
    )
    if int(major) <= int(m.group("major")):
        if minor != None:
            if int(minor) <= int(m.group("minor")):
                if patch_level != None:
                    if patch_level <= m.group("patchlevel"):
                        return True
                else:
                    return True
        else:
            return True
    return False


def get_next_free_vpc_domain_id(*, _requires=_get_missing_apic_connection_vars):
    data = query(
        "/api/node/class/fabricExplicitGEp.json?&order-by=fabricExplicitGEp.id|desc&page=0&page-size=1"
    )
    if data["totalCount"] == "1":
        return int(data["imdata"][0]["fabricExplicitGEp"]["attributes"]["id"]) + 1
    return 1


def get_access_aep_name_by_vlan_id(
    vlan_id, dn_filter="Access", *, _requires=_get_missing_apic_connection_vars
):
    try:
        access_aep = query(
            '/api/node/class/infraRsFuncToEpg.json?query-target-filter=and(wcard(infraRsFuncToEpg.dn,"{1}"),eq(infraRsFuncToEpg.encap,"vlan-{0}"),eq(infraRsFuncToEpg.mode,"untagged"))&order-by=infraRsFuncToEpg.dn'.format(
                vlan_id, dn_filter
            )
        )["imdata"][0]["infraRsFuncToEpg"]["attributes"]
        return access_aep["dn"].split("/")[2][8:]
    except IndexError:
        raise ValueError("no AEP for vlan id {0} found".format(vlan_id))


# def get_watcher_thread(url=None):
#     session=connect_apic()
#     if url:
#         thread=ACIWatcherThread(session,url)
#     else:
#         thread=ACIWatcherThread(session)
#     thread.start()
#     return thread


def get_all_vlans_from_pool(pool_name, *, _requires=_get_missing_apic_connection_vars):
    data = query(
        '/api/node/class/fvnsEncapBlk.json?query-target-filter=and(wcard(fvnsEncapBlk.dn,"{0}"))&order-by=fvnsEncapBlk.modTs|desc'.format(
            pool_name
        )
    )
    vlan_ids = []
    for block in data["imdata"]:
        from_id = int(block["fvnsEncapBlk"]["attributes"]["from"][5:])
        to_id = int(block["fvnsEncapBlk"]["attributes"]["to"][5:])
        vlan_ids = vlan_ids + list(range(from_id, to_id + 1))
    vlan_ids.sort()
    return vlan_ids


def vlan_pool_contains_vlan(pool_name, vlan_id):
    if vlan_id in get_all_vlans_from_pool(pool_name):
        return True
    else:
        return False


def dn_has_attribute(dn, key, value, *, _requires=_get_missing_apic_connection_vars):
    url = "/api/node/mo/{0}.json".format(dn)
    _jinjamator._log.debug(url)
    for obj in query(url)["imdata"]:
        for k, v in obj.items():
            try:
                if obj[k]["attributes"][key] != value:
                    return False
            except IndexError:
                return False
    return True


def get_all_configured_spine_uplinks(*, _requires=_get_missing_apic_connection_vars):
    infra_ports = {}
    try:

        infra_port_blks = query(
            "/api/node/class/infraSHPortS.json?query-target=children&target-subtree-class=infraPortBlk"
        )["imdata"]

        for infra_port_blk in infra_port_blks:
            info = query(
                "/api/node/mo/{}.json?rsp-subtree-include=full-deployment".format(
                    infra_port_blk["infraPortBlk"]["attributes"]["dn"]
                )
            )["imdata"][0]
            node_id = info["infraPortBlk"]["children"][0]["pconsNodeDeployCtx"][
                "attributes"
            ]["nodeId"]
            for card in range(
                int(infra_port_blk["infraPortBlk"]["attributes"]["fromCard"]),
                int(infra_port_blk["infraPortBlk"]["attributes"]["toCard"]) + 1,
            ):
                for interface in range(
                    int(infra_port_blk["infraPortBlk"]["attributes"]["fromPort"]),
                    int(infra_port_blk["infraPortBlk"]["attributes"]["toPort"]) + 1,
                ):
                    try:
                        infra_ports[node_id] += [(card, interface)]
                    except:
                        infra_ports[node_id] = [(card, interface)]
    except:
        pass

    return infra_ports


def get_all_fabric_ports(*, _requires=_get_missing_apic_connection_vars):
    fab_ports = query("/api/node/class/eqptFabP.json")["imdata"]
    retval = []
    for fab_port in fab_ports:
        #  'dn': 'topology/pod-1/node-1113/sys/ch/lcslot-1/lc/fabport-53',
        tmp = fab_port["eqptFabP"]["attributes"]["dn"].split("/")
        pod_id = tmp[1].split("-")[1]
        node_id = tmp[2].split("-")[1]
        slot = tmp[5].split("-")[1]
        port = fab_port["eqptFabP"]["attributes"]["id"]
        retval.append(
            {
                "node_id": node_id,
                "pod_id": pod_id,
                "port": port,
                "slot": slot,
                "interface_name": "eth{0}/{1}".format(slot, port),
                "long_interface_name": "Ethernet{0}/{1}".format(slot, port),
            }
        )
    return retval


def get_all_lldp_neighbours(*, _requires=_get_missing_apic_connection_vars):
    lldp_neighbours = query("/api/node/class/lldpAdjEp.json")["imdata"]
    retval = []
    # topology/pod-2/node-1223/sys/lldp/inst/if-[eth1/54]/adj-1
    localinterface_rgx = re.compile(r".+\[(\S+)\].+")
    for lldp_neighbour in lldp_neighbours:
        tmp = lldp_neighbour["lldpAdjEp"]["attributes"]["dn"].split("/")
        result = localinterface_rgx.match(
            lldp_neighbour["lldpAdjEp"]["attributes"]["dn"]
        )
        lldp_neighbour["lldpAdjEp"]["attributes"]["pod_id"] = tmp[1].split("-")[1]
        lldp_neighbour["lldpAdjEp"]["attributes"]["node_id"] = tmp[2].split("-")[1]
        lldp_neighbour["lldpAdjEp"]["attributes"]["interface_name"] = result.group(1)
        retval.append(lldp_neighbour["lldpAdjEp"]["attributes"])
    return retval


def get_all_nodes(index_by="id", *, _requires=_get_missing_apic_connection_vars):
    retval = {}
    fabric_nodes = query("/api/node/class/fabricNode.json")["imdata"]
    for node in fabric_nodes:
        retval[node["fabricNode"]["attributes"][index_by]] = node["fabricNode"][
            "attributes"
        ]
    return retval


def get_endpoint_table(*, _requires=_get_missing_apic_connection_vars):
    endpoint_data = {}
    vpc_fabric_path_ep_rxg = re.compile(
        r"topology/pod-(\d+)/protpaths-(\d+)-(\d+)/pathep-\[(.*)\]"
    )
    fabric_path_ep_rxg = re.compile(r"topology/pod-(\d+)/paths-(\d+)/pathep-\[(.*)\]")
    fex_fabric_path_ep_rxg = re.compile(
        r"topology/pod-(\d+)/paths-(\d+)/extpaths-(\d+)/pathep-\[(.*)\]"
    )

    for endpoint_obj in query(
        '/api/node/class/fvCEp.json?query-target-filter=not(wcard(fvCEp.dn,"__ui_"))&rsp-subtree=children&target-subtree-class=fvRsCEpToPathEp'
    )["imdata"]:
        ip = endpoint_obj["fvCEp"]["attributes"]["ip"]
        mac = endpoint_obj["fvCEp"]["attributes"]["mac"]
        encap = endpoint_obj["fvCEp"]["attributes"]["encap"]
        ep_dn = endpoint_obj["fvCEp"]["attributes"]["dn"]

        for path_obj in endpoint_obj["fvCEp"]["children"]:
            switch_a = None
            switch_b = None
            fex_id = None

            if "fvRsCEpToPathEp" in path_obj:
                path = path_obj["fvRsCEpToPathEp"]["attributes"]["tDn"]
                result = vpc_fabric_path_ep_rxg.match(path)
                if result:
                    pod_id, switch_a, switch_b, interface = result.groups()
                else:
                    result = fabric_path_ep_rxg.match(path)
                    if result:
                        pod_id, switch_a, interface = result.groups()
                        switch_b = None
                    else:
                        result = fex_fabric_path_ep_rxg.match(path)
                        if result:
                            pod_id, switch_a, fex_id, interface = result.groups()
                ds = {"ip": ip, "mac": mac, "encap": encap}
                if switch_a:
                    if switch_a not in endpoint_data:
                        endpoint_data[switch_a] = {}

                    if fex_id:
                        if fex_id not in endpoint_data[switch_a]:
                            endpoint_data[switch_a][fex_id] = {}
                            if interface not in endpoint_data[switch_a][fex_id]:
                                endpoint_data[switch_a][fex_id][interface] = []
                            endpoint_data[switch_a][fex_id][interface].append(ds)

                    if interface not in endpoint_data[switch_a]:
                        endpoint_data[switch_a][interface] = []
                    endpoint_data[switch_a][interface].append(ds)

                if switch_b:
                    if switch_b not in endpoint_data:
                        endpoint_data[switch_b] = {}
                    if interface not in endpoint_data[switch_b]:
                        endpoint_data[switch_b][interface] = []
                    endpoint_data[switch_b][interface].append(ds)
    return endpoint_data


def get_dict_from_epg_dn(dn):
    rgx = re.compile(r"uni/tn-(\S+)/ap-(\S+)/epg-(\S+)")
    result = rgx.match(dn)
    if result:
        return {
            "tenant_name": result.group(1),
            "ap_name": result.group(2),
            "epg_name": result.group(3),
        }
    else:
        return None


def get_dict_from_vrf_dn(dn):
    rgx = re.compile(r"uni/tn-(\S+)/ctx-(\S+)")
    result = rgx.match(dn)
    if result:
        return {"tenant_name": result.group(1), "vrf_name": result.group(2)}
    else:
        return None


def get_dict_from_external_epg_dn(dn):
    rgx = re.compile(r"uni/tn-(\S+)/out-(\S+)/instP-(\S+)")
    result = rgx.match(dn)
    if result:
        return {
            "tenant_name": result.group(1),
            "l3out_name": result.group(2),
            "external_epg_name": result.group(3),
        }
    else:
        return None


def get_dict_from_node_dn(dn):
    rgx = re.compile(r"topology/pod-(\S+)/node-(\S+)")
    result = rgx.match(dn)
    if result:
        return {"pod_id": result.group(1), "node_id": result.group(2)}
    else:
        return None
