from jinjamator.tools.rest_clients.jinjamator import (
    JinjamatorClient,
    JinjamatorResource,
)
from jinjamator.external.rest_client.exceptions import AuthError


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


admjmc.api.aaa.users.role_aaa_tester.roles.create(body={"role": "role_administration"})


try:
    response = jmc.api.aaa.roles.list()
except AuthError:
    raise ValueError(f"cannot list roles with role_administration role {response.body}")

admjmc.api.aaa.users.destroy("role_aaa_tester")


return "OK"
