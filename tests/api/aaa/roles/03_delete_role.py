from jinjamator.tools.rest_clients.jinjamator import JinjamatorClient
from jinjamator.external.rest_client.exceptions import NotFoundError

try:
    jmc = JinjamatorClient(
        f"http://localhost:{_container['port']}/api",
        ssl_verify=ssl_verify,
        username=_container["username"],
        password=_container["password"],
    )
    jmc.login()
except Exception as e:
    log.info(e)
    raise

response = jmc.api.aaa.roles.destroy("test")
if response.status_code != 204:
    raise ValueError(f"Unexpected response code {response.status_code}")

try:
    response = jmc.api.aaa.roles.retrieve("test")
    raise ValueError(f"Unexpected non empty return {response.body}")
except NotFoundError:
    pass


return "OK"
