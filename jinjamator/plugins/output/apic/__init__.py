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

import sys
import os
from jinjamator.tools.output_plugin_base import outputPluginBase, processError
from jinjamator.external.acitoolkit.acisession import Session
import getpass
from pprint import pformat
import json
from collections import defaultdict
import re
from pprint import pprint, pformat
import logging


def tree():
    return defaultdict(tree)


class apic(outputPluginBase):
    def __init__(self, parent):
        self._log = logging.getLogger()
        self._parent = parent
        self.apic_dn_acl_rules = [
            "uni/tn-\S+/ctx-.*,c,protect VRFs from deletion and configuration updates",
            "uni/tn-[a-zA-Z0-9]+$,c,protect Tenant objects from deletion",
        ]
        self._dn_acls = {}
        self.apic_password = ""
        self.apic_username = ""
        self.apic_key = ""
        self.apic_cert_name = ""
        self.apic_url = ""
        self.apic_session = None

    def addArguments(self):

        self._parent._parser.add_argument(
            "-l",
            "--apic-username",
            dest="apic_username",
            help="apic username [default: %(default)s]",
            default="admin",
        )
        self._parent._parser.add_argument(
            "-p",
            "--apic-password",
            dest="apic_password",
            help="apic password",
            default="",
        )
        self._parent._parser.add_argument(
            "-u", "--apic-url", dest="apic_url", help="apic URL", default=""
        )
        self._parent._parser.add_argument(
            "-k",
            "--apic-key",
            dest="apic_key",
            help="path to apic user private key",
            default="",
        )
        self._parent._parser.add_argument(
            "--apic-certname",
            dest="apic_cert_name",
            help="path to apic user certificate",
            default="",
        )
        self._parent._parser.add_argument(
            "--apic-set-dn-acl-rule",
            action="append",
            dest="apic_dn_acl_rules",
            help="format: <dn path regex>,<c(eate)|u(pdate)|d(delete)>,<remark> default: %(default)s",
            default=self.apic_dn_acl_rules,
        )

    def init_plugin_params(self, **kwargs):
        self._dn_acls = {}
        for var in [
            "apic_username",
            "apic_url",
            "apic_password",
            "apic_key",
            "apic_cert_name",
            "apic_dn_acl_rules",
        ]:
            if self._parent.configuration._data.get(var):
                setattr(self, var, self._parent.configuration._data.get(var, ""))

    @staticmethod
    def get_json_schema(configuration={}):
        # form = {
        #     "data": {
        #         "apic_cert_name": configuration.get("apic_cert_name", "")
        #     },
        #     "schema": {
        #         "type": "object",
        #         "title": "APIC Output Plugin Parameters",
        #         "properties": {
        #             "apic_cert_name": {
        #                 "title": "Cert Name",
        #                 "type": "string",
        #                 "description": "Name of the APIC user certificate",
        #             }
        #         },
        #     },
        #     "options": {
        #         "fields": {
        #             "apic_cert_name": {
        #                 "helper": [
        #                     "Name of the APIC user certificate"
        #                 ]
        #             }
        #         }
        #     },
        # }

        # return dict(form)
        form = tree()
        form["schema"]["type"] = "object"

        form["schema"]["properties"]["apic_cert_name"]["title"] = "Cert Name"
        form["schema"]["properties"]["apic_cert_name"]["type"] = "string"
        form["schema"]["properties"]["apic_cert_name"][
            "description"
        ] = "Name of the APIC user certificate"
        form["schema"]["properties"]["apic_cert_name"]["default"] = configuration.get(
            "apic_cert_name", ""
        )

        form["schema"]["properties"]["apic_key"]["title"] = "Key Path"
        form["schema"]["properties"]["apic_key"]["type"] = "string"
        form["schema"]["properties"]["apic_key"][
            "description"
        ] = "Server side path to encryption key for cert authentication (overrides password)"
        form["schema"]["properties"]["apic_key"]["default"] = configuration.get(
            "apic_key", ""
        )

        form["schema"]["properties"]["apic_password"]["title"] = "Password"
        form["schema"]["properties"]["apic_password"]["type"] = "string"
        form["schema"]["properties"]["apic_password"][
            "description"
        ] = "Cisco ACI password"
        form["schema"]["properties"]["apic_password"]["format"] = "password"
        form["schema"]["properties"]["apic_password"]["default"] = configuration.get(
            "apic_password", ""
        )

        form["schema"]["properties"]["apic_username"]["title"] = "Username"
        form["schema"]["properties"]["apic_username"]["type"] = "string"
        form["schema"]["properties"]["apic_username"][
            "description"
        ] = "Cisco ACI username"
        # form['schema']['properties']['apic_username']['required']=True
        form["schema"]["properties"]["apic_username"]["default"] = configuration.get(
            "apic_username", "admin"
        )

        form["schema"]["properties"]["apic_url"]["title"] = "APIC URL"
        form["schema"]["properties"]["apic_url"]["type"] = "string"
        form["schema"]["properties"]["apic_url"][
            "description"
        ] = "URL of Cisco ACI Controller"
        # form['schema']['properties']['apic_url']['required']=True
        # form["schema"]["properties"]["apic_url"]["default"] = configuration.get(
        #     "apic_url", "https://"
        # )

        form["schema"]["properties"]["apic_url"][
            "pattern"
        ] = "^(https?:\\/\\/)\
((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.?)+[a-z]*|\
((\\d{1,3}\\.){3}\\d{1,3}))\
(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*\
(\\?[;&a-z\\d%_.~+=-]*)?\
(\\#[-a-z\\d_]*)?$"
        form["schema"]["properties"]["apic_url"]["default"] = configuration.get(
            "apic_url", ""
        )

        form["options"]["fields"]["apic_url"]["order"] = 1
        # form["options"]['fields']['apic_url']['hideInitValidationError']= True
        form["options"]["fields"]["apic_username"]["order"] = 2
        form["options"]["fields"]["apic_password"]["order"] = 3
        form["options"]["fields"]["apic_key"]["order"] = 4
        form["options"]["fields"]["apic_cert_name"]["order"] = 5

        return dict(form)

    def connect(self, **kwargs):
        self.init_plugin_params()
        self.init_acls()
        if self.apic_key and self.apic_cert_name:
            self.apic_session = Session(
                self.apic_url,
                self.apic_username,
                cert_name=self.apic_cert_name,
                key=self.apic_key,
                subscription_enabled=False,
            )
        else:
            if not self.apic_password:
                self.apic_password = self._parent.handle_undefined_var("apic_password")

            self.apic_session = Session(
                self.apic_url,
                self.apic_username,
                self.apic_password,
                subscription_enabled=False,
            )
            self.apic_session.login()

    def init_acls(self):
        for apic_dn_acl_rule in self.apic_dn_acl_rules:
            if isinstance(apic_dn_acl_rule, str):
                dn_regex, flags, remark = apic_dn_acl_rule.split(",")
                self._dn_acls[dn_regex] = {
                    "rgx": re.compile(dn_regex),
                    "acls": {
                        "create": True if "c" in flags else False,
                        "read": True,
                        "update": True if "u" in flags else False,
                        "delete": True if "d" in flags else False,
                    },
                    "remark": remark,
                }
            elif isinstance(apic_dn_acl_rule, dict):
                self._dn_acls[apic_dn_acl_rule["regex"]] = {
                    "rgx": re.compile(apic_dn_acl_rule["regex"]),
                    "acls": {
                        "create": True
                        if "create" in apic_dn_acl_rule["acls"]
                        else False,
                        "read": True,
                        "update": True
                        if "update" in apic_dn_acl_rule["acls"]
                        else False,
                        "delete": True
                        if "delete" in apic_dn_acl_rule["acls"]
                        else False,
                    },
                    "remark": apic_dn_acl_rule.get("remark", ""),
                }

    def check_acl(self, item):
        obj_type = list(item.keys())[0]
        attributes = item[obj_type]["attributes"]

        for acl_string, acl in self._dn_acls.items():
            if acl["rgx"].match(attributes["dn"]):
                if (
                    attributes.get("status", "create") == "deleted"
                    and not acl["acls"]["delete"]
                ):
                    raise Exception(
                        "cannot delete dn {}, as it is forbidden by acl {}".format(
                            attributes["dn"], acl_string
                        )
                    )
                elif acl["acls"]["create"] and acl["acls"]["update"]:
                    return True
                existing_data = json.loads(
                    self.apic_session.get(
                        "/api/node/mo/{0}.json".format(attributes["dn"])
                    ).text
                )
                if len(existing_data["imdata"]) > 0 and acl["acls"]["update"]:
                    return True
                elif len(existing_data["imdata"]) == 0 and acl["acls"]["create"]:
                    return True
                else:
                    raise Exception(
                        "cannot create or update dn {}, as it is forbidden by acl {} {}".format(
                            attributes["dn"], acl_string, pformat(acl["acls"])
                        )
                    )

            else:
                self._log.debug(
                    "no acl match  acl {}  dn {}".format(acl_string, attributes["dn"])
                )

    def process(self, data, **kwargs):

        try:
            if data in [None, "None", ""]:
                self._log.debug("empty document -> nothing to do -> skipping")
                return True

            data = json.loads(data)
            self._log.debug(json.dumps(data, indent=2))
        except ValueError as e:
            self._log.error(
                "{0}\nis not a valid json document {1} -> invalid configuration -> skipping".format(
                    data, e
                )
            )
            return False
        except TypeError:
            pass
        for item in data["imdata"]:
            try:
                dn = item[list(item.keys())[0]]["attributes"]["dn"]
                self.check_acl(item)
            except IndexError:
                continue
            resp = self.apic_session.push_to_apic(
                "/api/node/mo/{0}.json".format(dn), item, timeout=None
            )
            if not resp.ok:
                self._log.error("POST request failed: {0}".format(pformat(resp.text)))
                self._log.debug(pformat(item))
                if "best_effort" in self._parent.configuration._data.keys():
                    return True
                raise processError

            else:
                self._log.info("successfully sent config for dn {0}".format(dn))
                self._log.debug(json.dumps(item, indent=2))
        return True
