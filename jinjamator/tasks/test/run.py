from jinjamator.tools.rest_clients.jinjamator import JinjamatorClient
from time import sleep

jm = JinjamatorClient(
    "https://localhost:5000/api",
    ssl_verify="/home/putzw/git/jinjamator/avl-test/ssl/localhost.crt",
)
jm.login("root", "ciscocisco")

while True:
    print(jm.api.aaa.users.retrieve("1/roles").headers)
    print(jm.api.aaa.users.list().headers)
    # print(jm.api.aaa.users.retrieve("1/roles").body)
    sleep(1)
