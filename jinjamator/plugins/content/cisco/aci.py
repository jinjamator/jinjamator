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
    "N2K-B22HP-P": {
        "uplinks": range(17, 25),
        "downlinks": range(1, 17),
        "type": "fex",
    },
    "N2K-C2248TP-1GE": {
        "uplinks": range(49, 53),
        "downlinks": range(1, 49),
        "type": "fex",
    },
    "N9K-C9364C": {"uplinks": [], "downlinks": range(1, 67), "type": "spine",},
    "N9K-C9332C": {"uplinks": [], "downlinks": range(1, 35), "type": "spine",},
    "N9K-C9336PQ": {"uplinks": [], "downlinks": range(1, 37), "type": "spine",},
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
}

log = logging.getLogger()


def connect_apic(subscription_enabled=False):
    if not self._parent.configuration["apic_url"]:
        self._parent.handle_undefined_var("apic_url")
    if not self._parent.configuration["apic_username"]:
        self._parent.handle_undefined_var("apic_username")
    if not self._parent.configuration["apic_key"]:
        del self._parent.configuration["apic_key"]
    if not self._parent.configuration["apic_cert_name"]:
        del self._parent.configuration["apic_cert_name"]
    if (
        "apic_key" in self._parent.configuration.keys()
        and "apic_cert_name" in self._parent.configuration.keys()
    ):
        apic_session = Session(
            self._parent.configuration["apic_url"],
            self._parent.configuration["apic_username"],
            cert_name=self._parent.configuration["apic_cert_name"],
            key=self._parent.configuration["apic_key"],
            subscription_enabled=False,
        )
    else:
        if not self._parent.configuration["apic_password"]:
            self._parent.handle_undefined_var("apic_password")
        apic_session = Session(
            self._parent.configuration["apic_url"],
            self._parent.configuration["apic_username"],
            self._parent.configuration["apic_password"],
            subscription_enabled=subscription_enabled,
        )
        apic_session.login()
    return apic_session


def query(queryURL):
    if "subscription=yes" in queryURL:
        subscription_enabled = True
    else:
        subscription_enabled = False
    session = connect_apic(subscription_enabled)
    data = session.get(queryURL)
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
    return switchdb[model.upper()]["downlinks"]


def get_parent_dn_from_child_dn(dn):
    dn = re.sub(r"\[\S+\]", "", dn)
    tmp = dn.split("/")
    return "/".join(tmp[:-1])


def is_dn_in_use(dn, ignore_children=False):
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


def dn_exists(dn):
    data = query("/api/node/mo/{0}.json".format(dn))
    if int(data["totalCount"]) > 0:
        return True
    return False


def get_podid_by_switch_id(switch_id):
    data = query(
        '/api/node/class/fabricNode.json?query-target-filter=and(eq(fabricNode.id,"{0}"))'.format(
            switch_id
        )
    )
    return (
        get_parent_dn_from_child_dn(data["imdata"][0]["fabricNode"]["attributes"]["dn"])
        .split("/")[-1:][0]
        .split("-")[1]
    )


def version(node_id=1):
    pod_id = get_podid_by_switch_id(node_id)
    data = query(
        "/api/node/class/topology/pod-{0}/node-{1}/firmwareCtrlrRunning.json".format(
            pod_id, node_id
        )
    )
    return data["imdata"][0]["firmwareCtrlrRunning"]["attributes"]["version"]


def is_min_version(major, minor, patch_level, node_id=1):
    """
    {% if aci_is_min_version(4, 0, None) %}
    {% endif %}
    """
    running_version = aci_version(node_id)
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


def get_next_free_vpc_domain_id():
    data = query(
        "/api/node/class/fabricExplicitGEp.json?&order-by=fabricExplicitGEp.id|desc&page=0&page-size=1"
    )
    if data["totalCount"] == "1":
        return int(data["imdata"][0]["fabricExplicitGEp"]["attributes"]["id"]) + 1
    return 1


def get_access_aep_name_by_vlan_id(vlan_id, dn_filter="Access"):
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


def get_all_vlans_from_pool(pool_name):
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


def dn_has_attribute(dn, key, value):
    url = "/api/node/mo/{0}.json".format(dn)
    self._parent._log.debug(url)
    for obj in query(url)["imdata"]:
        for k, v in obj.items():
            try:
                if obj[k]["attributes"][key] != value:
                    return False
            except IndexError:
                return False
    return True


def get_all_configured_spine_uplinks():
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


def get_all_fabric_ports():
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


def get_all_lldp_neighbours():
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


def get_all_nodes(index_by="id"):
    retval = {}
    fabric_nodes = query("/api/node/class/fabricNode.json")["imdata"]
    for node in fabric_nodes:
        retval[node["fabricNode"]["attributes"][index_by]] = node["fabricNode"][
            "attributes"
        ]
    return retval


def get_endpoint_table():
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
