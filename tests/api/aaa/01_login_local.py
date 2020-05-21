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


return "OK"
