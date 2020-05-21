from jinjamator.tools.rest_clients.jinjamator import JinjamatorClient

log.info(f"http://localhost:{_container['port']}/api")

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

roles = [item["name"] for item in jmc.api.aaa.roles.list().body]

roles.remove("administrator")
roles.remove("operator")
roles.remove("role_administration")
roles.remove("user_administration")

if len(roles) != 0:
    raise ValueError(f"found undefined roles {roles}")

return "OK"
