from jinjamator.external.rest_client.api import API
import logging
from pprint import pformat
from jinjamator.external.rest_client.resource import Resource
from jinjamator.external.rest_client.request import make_request
from jinjamator.external.rest_client.models import Request
from types import MethodType


class CiscoTokenAPIResource(Resource):
    pass


class CiscoSupportAPI(Resource):
    def add_action(self, action_name):
        def action_method(
            self,
            *args,
            body=None,
            params=None,
            headers=None,
            action_name=action_name,
            **kwargs,
        ):
            url = self.get_action_full_url(action_name, *args)
            method = self.get_action_method(action_name)
            request = Request(
                url=url,
                method=method,
                params=params or {},
                body=body,
                headers=headers or {},
                timeout=self.timeout,
                ssl_verify=self.ssl_verify,
                kwargs=kwargs,
            )

            request.params.update(self.params)
            request.headers.update(self.headers)
            response = make_request(self.client, request)
            # if response.headers.get("Authorization"):
            #     self.headers["Authorization"] = response.headers["Authorization"]
            return response

        setattr(self, action_name, MethodType(action_method, self))


class CiscoSupportAPIClient(object):
    def __init__(self, url="https://api.cisco.com/", **kwargs):
        self._log = logging.getLogger()
        self._base_url = url
        self._grant_type = kwargs.get("grant_type", "client_credentials")
        self._login_url = kwargs.get("login_url", "https://cloudsso.cisco.com/as/")
        # /as/token.oauth2
        self.tokenapi = API(
            api_root_url=self._login_url,  # base api url
            params={},  # default params
            headers={},  # default headers
            timeout=10,  # default timeout in seconds
            append_slash=False,  # append slash to final url
            json_encode_body=True,  # encode body as json
            ssl_verify=kwargs.get("ssl_verify", True),
            resource_class=CiscoTokenAPIResource,
        )
        self.tokenapi.add_resource(
            self._login_url, "token.oauth2", CiscoTokenAPIResource
        )

        self.api = API(
            api_root_url=url,  # base api url
            params={},  # default params
            headers={},  # default headers
            timeout=10,  # default timeout in seconds
            append_slash=False,  # append slash to final url
            json_encode_body=True,  # encode body as json
            ssl_verify=kwargs.get("ssl_verify", True),
            resource_class=CiscoSupportAPI,
        )

    def __str__(self):
        return pformat(self.api.get_resource_list())

    def login(self, client_id=None, client_secret=None):
        if client_id:
            self._client_id = client_id
        if client_secret:
            self._client_secret = client_secret
        # token.oauth2

        auth_data = (
            self.tokenapi._resources["token.oauth2"]
            .create(
                params={
                    "grant_type": self._grant_type,
                    "client_id": client_id,
                    "client_secret": client_secret,
                }
            )
            .body
        )

        token = auth_data.get("access_token")
        self.api.headers["Authorization"] = f"Bearer {token}"
        return True


# test=CiscoSupportAPIClient()
# test.login("asdf","qwer")
# print(test.api.bug('v3.0').bugs.bug_ids.CSCwc66053.list())
