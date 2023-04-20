import docker.api.build
import docker
from docker.errors import ImageNotFound, BuildError
from io import StringIO
import sys

docker.api.build.process_dockerfile = lambda dockerfile, path: (
    "Dockerfile",
    dockerfile,
)


tag = baseimage
client = docker.from_env()


try:
    client.images.get(tag)
    log.info(f"base image {tag} found")
    if force_rebuild:
        log.info("force_rebuild set -> rebuilding")
        raise ImageNotFound("force_rebuild set -> rebuilding")
except ImageNotFound:
    log.info("base image not found building")
    docker_file = task.run("dockerfile", output_plugin="null")[0]["result"]
    log.debug(docker_file)
    try:
        image, logs = client.images.build(
            path=".", dockerfile=docker_file, tag=tag, nocache=True
        )
    except BuildError as e:
        # for line in logs:
        #    log.debug(line)
        log.error(e)
        raise

    for line in logs:
        log.debug(line)
    log.info(f"finished building {tag}")
