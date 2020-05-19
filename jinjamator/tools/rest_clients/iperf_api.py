from jinjamator.external.rest_client.api import API
from jinjamator.external.rest_client.resource import Resource
import logging
from pprint import pformat


class RunState(Resource):
    @property
    def default_actions(self):
        return {
            "start": {"method": "POST", "url": "{0}/start".format(self.resource_name)},
            "stop": {"method": "POST", "url": "{0}/stop".format(self.resource_name)},
            "results": {
                "method": "GET",
                "url": "{0}/results".format(self.resource_name),
            },
            "destroy": {"method": "DELETE", "url": "{0}".format(self.resource_name)},
        }


def get_iperf_api_client(url, ssl_verify=False):
    _log = logging.getLogger("")
    api = API(
        api_root_url=url,  # base api url
        params={},  # default params
        headers={},  # default headers
        timeout=10,  # default timeout in seconds
        append_slash=False,  # append slash to final url
        json_encode_body=True,  # encode body as json
        ssl_verify=ssl_verify,
    )

    api.add_resource(resource_name="servers")
    api.add_resource(resource_name="clients")
    api.add_resource(resource_name="system/network/interfaces")
    for vrf, interfaces in api.system.network.interfaces.list().body.items():
        for interface in interfaces:
            api.add_resource(
                resource_name="system/network/interfaces/{0}/{1}".format(vrf, interface)
            )
        api.add_resource(resource_name="system/network/{0}/routes".format(vrf))
    _log.debug(pformat(api.get_resource_list()))
    return api
