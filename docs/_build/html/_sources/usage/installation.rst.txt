Installation
==================


How to install
--------------

To install the latest stable version jinjamator you should use the pypi or the docker release.

For a local install just run:

.. code:: shell

    pip3 install jinjamator

This should automatically setup jinjamator.

To run the docker container it is suggested to use docker-compose or kubernetes.

.. code-block:: yaml

    version: '3.3'
    services:
        nginx-proxy:
            image: jwilder/nginx-proxy
            ports:
                - "80:80"
                - "443:443"
            volumes:
                - /var/run/docker.sock:/tmp/docker.sock:ro
                - /opt/jinjamator/.ssl:/etc/nginx/certs
        jinjamator:
            restart: always
            depends_on:
                - nginx-proxy
            container_name: jinjamator
            image: jinjamator/jinjamator:latest
            volumes:
                - /opt/jinjamator:/root/.jinjamator
            environment:
                - VIRTUAL_HOST=localhost
                - VIRTUAL_PORT=5000
                - HTTPS_METHOD=redirect
                - JINJAMATOR_AAA_LOCAL_ADMIN_PASSWORD=password
                - JINJAMATOR_AAA_LOCAL_ADMIN_USERNAME=admin
                - JINJAMATOR_DAEMON_LISTEN_ADDRESS=0.0.0.0
                - JINJAMATOR_DAEMON_SECRET_KEY=thisisinsecurebutforlocaldevelopmentok