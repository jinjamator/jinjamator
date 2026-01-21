# Copyright 2026 Wilhelm Putz

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

import os
import logging

log = logging.getLogger()


def _get_missing_cc_connection_vars():
    inject = []
    try:
        if not _jinjamator.configuration._data.get("cc_username"):
            inject.append("cc_username")
        if not _jinjamator.configuration._data.get("cc_password"):
            inject.append("cc_password")
        if not _jinjamator.configuration._data.get("cc_url"):
            inject.append("cc_url")
    except Exception as e:
        log.error(e)
        pass
    return inject


def connect(*, _requires=_get_missing_cc_connection_vars, **kwargs):
    """Connect to a Cisco Catalyst Center.
    :return: returns a logged in simple-catalyst-center object

    :Keyword Arguments:
        * *cc_username* (``str``), ``optional``, ``jinjamator enforced`` --
           Username for the CC connection. If not set in task configuration or via keyword argument jinjamator asks the user to input the data.
        * *cc_password* (``str``), ``optional``, ``jinjamator enforced`` --
           Password for the CC connection. If not set in task configuration or via keyword argument jinjamator asks the user to input the data.
        * *cc_url*  (``str``), ``optional``, ``jinjamator enforced`` --
           Target URL for the CC connection. If not set in task configuration or via keyword argument jinjamator asks the user to input the data.
    
    :Examples:
        If one of the following conditions are met,
            * *cc_username*, *cc_password*, *cc_url* is specified via command line parameter in CLI Mode e.g -m 'cc_username':'admin'
            * Any of *cc_username*, *cc_password*, *cc_url* is not specified via command line parameter in CLI Mode and the user enters the data correctly via CLI.
            * The task is run via Daemon mode and cc_username, cc_password, cc_url are defined in the task defaults.yaml, environment site defaults.yaml.
            * The task is run via Daemon mode and cc_username, cc_password, cc_url are entered correctly in the generated webform.



    """

    try:
        from simple_catalyst_center import CiscoCatalystCenterClient
    except ImportError:
        log.error("cannot load simple-catalyst-center. Please install simple-catalyst-center into the jinjamator environment by running pipx inject jinjamator simple-catalyst-center.")
        return None


    cc_url=kwargs.get("cc_url",_jinjamator.configuration._data.get("cc_url","<not set>"))
    cc_username=kwargs.get("cc_username",_jinjamator.configuration._data.get("cc_username","<not set>"))
    cc_password=kwargs.get("cc_password",_jinjamator.configuration._data.get("cc_password","<not set>"))

    cc = CiscoCatalystCenterClient(cc_url, **kwargs)
    try:
        cc.login(cc_username, cc_password)
    except Exception as e:
        log.error(e)
        return None
    return cc


def disconnect(connection):
    pass
