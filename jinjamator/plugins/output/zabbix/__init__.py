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

from pprint import pformat
import json
from collections import defaultdict
import re
from pprint import pprint, pformat
import logging
from pyzabbix import ZabbixMetric, ZabbixSender


def tree():
    return defaultdict(tree)


class zabbix(outputPluginBase):
    def __init__(self, parent):
        self._log = logging.getLogger()
        self._parent = parent

    def addArguments(self):

        self._parent._parser.add_argument(
            "--zabbix-server",
            dest="zabbix_server",
            help="Zabbix server hostname or IP [default: %(default)s]",
            default="127.0.0.1",
        )
        self._parent._parser.add_argument(
            "--zabbix-server-port",
            dest="zabbix_port",
            help="Zabbix server port [default: %(default)s]",
            default=10051,
        )
        self._parent._parser.add_argument(
            "--zabbix-host",
            dest="zabbix_host",
            help="Hostname as it displayed in Zabbix [default: %(default)s]",
            default="",
        )

    def init_plugin_params(self, **kwargs):

        for var in ["zabbix_server", "zabbix_port", "zabbix_host"]:
            if self._parent.configuration._data.get(var):
                setattr(self, var, self._parent.configuration._data.get(var, ""))

    @staticmethod
    def get_json_schema(configuration={}):

        form = tree()
        form["schema"]["type"] = "object"

        form["schema"]["properties"]["zabbix_server"]["title"] = "Zabbix Server"
        form["schema"]["properties"]["zabbix_server"]["type"] = "string"
        form["schema"]["properties"]["zabbix_server"][
            "description"
        ] = "Zabbix server hostname or IP"

        form["schema"]["properties"]["zabbix_port"]["title"] = "Port"
        form["schema"]["properties"]["zabbix_port"]["type"] = "integer"
        form["schema"]["properties"]["zabbix_port"][
            "description"
        ] = "Zabbix server port"

        form["schema"]["properties"]["zabbix_port"]["default"] = configuration.get(
            "zabbix_port", 10051
        )

        form["schema"]["properties"]["zabbix_host"]["title"] = "Zabbix Hostname"
        form["schema"]["properties"]["zabbix_host"]["type"] = "string"
        form["schema"]["properties"]["zabbix_host"][
            "description"
        ] = "Hostname as it displayed in Zabbix"
        form["schema"]["properties"]["zabbix_host"]["default"] = configuration.get(
            "zabbix_host", ""
        )

        form["options"]["fields"]["zabbix_server"]["order"] = 1

        form["options"]["fields"]["zabbix_port"]["order"] = 2
        form["options"]["fields"]["zabbix_host"]["order"] = 3

        return dict(form)

    def connect(self, **kwargs):
        self.init_plugin_params()
        self.zbx = ZabbixSender(
            self._parent.configuration._data.get("zabbix_server"),
            self._parent.configuration._data.get("zabbix_port"),
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

        metrics = []
        for row in data:
            target_hostname = row.get(
                "hostname", self._parent.configuration._data.get("zabbix_host", None)
            )
            if target_hostname:
                for k, v in row.items():
                    if k not in ["hostname"]:
                        m = ZabbixMetric(target_hostname, k, v)
                        metrics.append(m)
            else:
                log.error("Target Hostname not defined -> skipping")
                log.debug(row)
        self.zbx.send(metrics)

        # for item in data["imdata"]:
        #     try:
        #         dn = item[list(item.keys())[0]]["attributes"]["dn"]
        #         self.check_acl(item)
        #     except IndexError:
        #         continue
        #     resp = self.apic_session.push_to_apic(
        #         "/api/node/mo/{0}.json".format(dn), item, timeout=None
        #     )
        #     if not resp.ok:
        #         self._log.error("POST request failed: {0}".format(pformat(resp.text)))
        #         self._log.debug(pformat(item))
        #         if "best_effort" in self._parent.configuration._data.keys():
        #             return True
        #         raise processError

        #     else:
        #         self._log.info("successfully sent config for dn {0}".format(dn))
        #         self._log.debug(json.dumps(item, indent=2))
        return True
