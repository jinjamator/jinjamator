from jinjamator.external.rest_client.api import API
import logging
from pprint import pformat
from jinjamator.external.rest_client.resource import Resource
from jinjamator.external.rest_client.request import make_request
from jinjamator.external.rest_client.models import Request
from types import MethodType
from datetime import datetime


class NexusDashboardNIRParameterException(Exception):
    pass


class NexusDashboardResource(Resource):
    pass


class NexusDashboardNIRResource(NexusDashboardResource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        group_name = kwargs.get("group_name", "") or self.params.get(
            "insightsGroupName"
        )
        if not group_name:
            raise NexusDashboardNIRParameterException(
                "group_name (insightsGroupName) must be set"
            )
        self.params["insightsGroupName"] = group_name

        try:
            self.params["startTs"] = kwargs["start"]
        except KeyError:
            logging.debug(
                "neither startTs nor start is set using 1970-01-01T00:00:00+00:00 for startTs"
            )
            self.params["startTs"] = "1970-01-01T00:00:00+00:00"
        try:
            self.params["endTs"] = kwargs["end"]
        except KeyError:
            now = datetime.now()
            iso = now.isoformat(timespec="seconds")
            logging.debug(f"neither endTs nor end is set using now {iso} for endTs")
            self.params["endTs"] = iso


class NexusDashboardClient(object):
    def __init__(self, url, **kwargs):
        self._log = logging.getLogger()
        self._base_url = url
        self._username = kwargs.get("username", None)
        self._password = kwargs.get("password", None)
        self.dashboard = API(
            api_root_url=url,  # base api url
            params={},  # default params
            headers={},  # default headers
            timeout=10,  # default timeout in seconds
            append_slash=False,  # append slash to final url
            json_encode_body=True,  # encode body as json
            ssl_verify=kwargs.get("ssl_verify", None),
            resource_class=NexusDashboardResource,
        )
        self.nir = API(
            api_root_url=url + "/sedgeapi/v1/cisco-nir/api/api/",  # base api url
            params={},  # default params
            headers={},  # default headers
            timeout=10,  # default timeout in seconds
            append_slash=False,  # append slash to final url
            json_encode_body=True,  # encode body as json
            ssl_verify=kwargs.get("ssl_verify", None),
            resource_class=NexusDashboardNIRResource,
            ep_suffix=".json",
        )

        self._apis = {"dashboard": self.dashboard, "nir": self.nir}

    def __str__(self):
        retval = {}
        for apiname, api in self._apis.items():
            retval[apiname] = api.get_resource_list()
        return pformat(retval)

    def login(self, username=None, password=None):
        if username:
            self._username = username
        if password:
            self._password = password

        auth_data = self.dashboard.login.create(
            body={
                "userName": self._username,
                "userPasswd": self._password,
                "domain": "DefaultAuth",
            }
        ).body

        token = auth_data.get("jwttoken")
        for apiname, api in self._apis.items():
            api.headers["Authorization"] = "Bearer " + token

        return True


# nd=NexusDashboardClient("https://100.76.246.11", ssl_verify=False)

# nd.login("admin","asdf")
# nd.nir.params["insightsGroupName"]="noone"
# for item in nd.nir.telemetry.nodes.list().body.get("entries",[]):
#     print(item["nodeName"])
# # return nd.nir.telemetry.advisories.details.list().body
