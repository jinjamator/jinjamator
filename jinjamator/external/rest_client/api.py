from .resource import Resource
import logging


class API:
    def __init__(
        self,
        api_root_url=None,
        params=None,
        headers=None,
        timeout=None,
        append_slash=False,
        json_encode_body=False,
        ssl_verify=None,
        resource_class=None,
        ep_suffix="",
        **kwargs
    ):
        self.api_root_url = api_root_url
        self.params = params or {}
        self.headers = headers or {}
        self.timeout = timeout
        self.append_slash = append_slash
        self.json_encode_body = json_encode_body
        self.ssl_verify = True if ssl_verify is None else ssl_verify
        self._resources = {}
        self._resource_class = resource_class or Resource
        self._log = logging.getLogger(__file__)
        self._ep_suffix = ep_suffix
        self._kwargs = kwargs
        if self.json_encode_body:
            self.headers["Content-Type"] = "application/json"

    def add_resource(
        self,
        api_root_url=None,
        resource_name=None,
        resource_class=None,
        params=None,
        headers=None,
        timeout=None,
        append_slash=False,
        json_encode_body=False,
    ):
        if "/" in resource_name:
            resources = resource_name.split("/")
        else:
            resources = [resource_name]
        parent = self
        resource_name = ""
        for objname in resources:
            resource_name = "{0}/{1}".format(resource_name, objname)
            resource_class = resource_class or self._resource_class
            resource = resource_class(
                api_root_url=api_root_url or self.api_root_url,
                resource_name=resource_name,
                params=params or self.params,
                headers=headers or self.headers,
                timeout=timeout or self.timeout,
                append_slash=append_slash or self.append_slash,
                json_encode_body=json_encode_body or self.json_encode_body,
                ssl_verify=self.ssl_verify,
                **self._kwargs
            )
            if not getattr(parent, objname, None):
                setattr(parent, objname, resource)
            else:
                resource = getattr(parent, objname)
            parent = resource
            self._resources[resource_name] = resource

    def get_resource_list(self):
        return list(self._resources.keys())

    def __getattr__(self, instance):
        self._resources[instance] = self._resource_class(
            api_root_url=self.api_root_url,
            resource_name=instance,
            params=self.params,
            headers=self.headers,
            timeout=self.timeout,
            append_slash=self.append_slash,
            json_encode_body=self.json_encode_body,
            ssl_verify=self.ssl_verify,
            ep_suffix=self._ep_suffix,
            **self._kwargs
        )
        setattr(self, instance, self._resources[instance])

        return self._resources[instance]
