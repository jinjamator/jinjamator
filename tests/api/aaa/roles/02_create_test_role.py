from jinjamator.tools.rest_clients.jinjamator import JinjamatorClient


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

response = jmc.api.aaa.roles.create(body={"name": "test"})
if response.status_code != 201:
    raise ValueError(f"Unexpected response code {response.status_code}")


return "OK"
