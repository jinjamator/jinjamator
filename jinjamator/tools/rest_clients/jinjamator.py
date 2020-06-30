from jinjamator.external.rest_client.api import API
import logging
from pprint import pformat
from jinjamator.external.rest_client.resource import Resource
from jinjamator.external.rest_client.request import make_request
from jinjamator.external.rest_client.models import Request
from types import MethodType


class JinjamatorResource(Resource):
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
            if response.headers.get("Authorization"):
                self.headers["Authorization"] = response.headers["Authorization"]
            return response

        setattr(self, action_name, MethodType(action_method, self))


class JinjamatorClient(object):
    def __init__(self, url, **kwargs):
        self._log = logging.getLogger()
        self._base_url = url
        self._username = kwargs.get("username", None)
        self._password = kwargs.get("password", None)
        self.api = API(
            api_root_url=url,  # base api url
            params={},  # default params
            headers={},  # default headers
            timeout=10,  # default timeout in seconds
            append_slash=False,  # append slash to final url
            json_encode_body=True,  # encode body as json
            ssl_verify=kwargs.get("ssl_verify", None),
            resource_class=JinjamatorResource,
        )

    def __str__(self):
        return pformat(self.api.get_resource_list())

    def login(self, username=None, password=None):
        if username:
            self._username = username
        if password:
            self._password = password

        auth_data = self.api.aaa.login.local.list(
            params={"username": self._username, "password": self._password}
        ).body
        token = auth_data.get("access_token")
        self.api.headers["Authorization"] = token
        return True
