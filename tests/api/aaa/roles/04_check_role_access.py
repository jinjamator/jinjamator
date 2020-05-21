from jinjamator.tools.rest_clients.jinjamator import JinjamatorClient
from jinjamator.external.rest_client.exceptions import AuthError

log.info(f"http://localhost:{_container['port']}/api")

try:
    admjmc = JinjamatorClient(
        f"http://localhost:{_container['port']}/api",
        ssl_verify=ssl_verify,
        username=_container["username"],
        password=_container["password"],
    )
    admjmc.login()
except Exception as e:
    log.info(e)
    raise

password = jm.password.generate(16)
admjmc.api.aaa.users.create(
    body={"username": "role_aaa_tester", "name": "unit test user", "password": password}
)

try:
    jmc = JinjamatorClient(
        f"http://localhost:{_container['port']}/api",
        ssl_verify=ssl_verify,
        username="role_aaa_tester",
        password=password,
    )
    jmc.login()
except Exception as e:
    log.info(e)
    raise

try:
    response = jmc.api.aaa.roles.list()
    raise ValueError(f"Unexpected non empty return {response.body}")
except AuthError:
    pass

# admjmc.api.aaa.users.delete('role_aaa_tester') not yet implemented


return "OK"
