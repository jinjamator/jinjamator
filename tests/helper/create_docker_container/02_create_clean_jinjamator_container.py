import docker
import atexit
import re
from colorama import Fore, Style


def cleanup(container):
    print("stopping test container:", end=" ")
    container.stop()
    print(Fore.GREEN + "DONE" + Style.RESET_ALL)
    print("deleting test container:", end=" ")
    container.remove()
    print(Fore.GREEN + "DONE" + Style.RESET_ALL)


client = docker.from_env()

command = [
    "/bin/sh",
    "-c",
    "cp /opt/jinjamator/bin/jinjamator /usr/local/bin \
    && chmod ugo+x /usr/local/bin/jinjamator \
    && pip3 install --no-warn-script-location -r /opt/jinjamator/requirements.txt \
    && cd /opt/jinjamator \
    && ./bin/jinjamator -t jinjamator/tasks/.internal/init_aaa -vvv\
    && ./bin/jinjamator -d -vvvv",
]

env = {line.split("=")[0]: line.split("=")[1] for line in environment}

log.info(f"creating container")

container = client.containers.run(
    baseimage,
    detach=True,
    volumes=volumes,
    ports=ports,
    command=command,
    environment=environment,
)

ready_rgx = re.compile(r".*Debugger PIN:.*")

for logline in container.logs(stream=True):
    logline = logline.decode("utf-8")
    log.debug(logline)
    if ready_rgx.match(logline):
        log.info(f"container ready {container.id}")
        break


atexit.register(cleanup, container)

retval = {
    "id": container.id,
    "port": client.containers.get(container.id).ports["5000/tcp"][0]["HostPort"],
    "secret": env["JINJAMATOR_DAEMON_SECRET_KEY"],
    "username": env["JINJAMATOR_AAA_LOCAL_ADMIN_USERNAME"],
    "password": env["JINJAMATOR_AAA_LOCAL_ADMIN_PASSWORD"],
}

return retval
