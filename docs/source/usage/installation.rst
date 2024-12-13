Installation
==================


How to install
--------------

To install the latest stable version jinjamator you should use the pypi or the docker release.

For a local install just run:

.. code:: shell

    pip install pipx && pipx install jinjamator

After successfull installation you should run following commands to initialize aaa

.. code:: shell

    export JINJAMATOR_AAA_LOCAL_ADMIN_USERNAME=admin
    export JINJAMATOR_AAA_LOCAL_ADMIN_PASSWORD=SomeSecurePassword
    jinjamator -t `pipx runpip jinjamator show jinjamator | grep Location | cut -d ' ' -f 2`/jinjamator/tasks/.internal/init_aaa


to use LDAP for aaa you can define additional shell variables and run or rerun the init_aaa task

.. code:: shell

    # configure a local admin
    export JINJAMATOR_AAA_LOCAL_ADMIN_USERNAME=admin
    export JINJAMATOR_AAA_LOCAL_ADMIN_PASSWORD=SomeSecurePassword
    # create a LDAP login domain with the name THENAMEFORTHELDAPDOMAIN
    export JINJAMATOR_AAA_THENAMEFORTHELDAPDOMAIN_TYPE=LDAP
    # use SSL and 2 Domain Controllers
    export JINJAMATOR_AAA_THENAMEFORTHELDAPDOMAIN_SERVER1_NAME=1.2.3.4
    export JINJAMATOR_AAA_THENAMEFORTHELDAPDOMAIN_SERVER1_PORT=636
    export JINJAMATOR_AAA_THENAMEFORTHELDAPDOMAIN_SERVER1_SSL=True
    export JINJAMATOR_AAA_THENAMEFORTHELDAPDOMAIN_SERVER2_NAME=5.6.7.8
    export JINJAMATOR_AAA_THENAMEFORTHELDAPDOMAIN_SERVER2_PORT=636
    export JINJAMATOR_AAA_THENAMEFORTHELDAPDOMAIN_SERVER2_SSL=True
    # define the AD domain
    export JINJAMATOR_AAA_THENAMEFORTHELDAPDOMAIN_DOMAIN=somedomain.local
    # define the search base for users
    export JINJAMATOR_AAA_THENAMEFORTHELDAPDOMAIN_USER_BASE_DN=DC=somedomain,DC=local
    # you have to define which groups are allowed to login
    # To define multiple groups just keep increasing the GROUP<N>
    export JINJAMATOR_AAA_THENAMEFORTHELDAPDOMAIN_ALLOWED_GROUP1=CN=test_group,OU=Groups,DC=somedomain,DC=local
    export JINJAMATOR_AAA_THENAMEFORTHELDAPDOMAIN_ALLOWED_GROUP2=CN=test_group2,OU=Groups,DC=somedomain,DC=local
    # LDAP Groups must be mapped to jinjamator roles (in jinjamator there is a role for almost everything)
    # This allows the test_group to login, use the task demotask and the environment site DEMO/SITE1
    export JINJAMATOR_AAA_THENAMEFORTHELDAPDOMAIN_ALLOWED_GROUP1_MAP=operator,task_demotask,environment_DEMO|site_SITE1
    # This allows the test_group2 to login, use all tasks below taskcollection1/subdir2, demotask2 and the environment site DEMO/SITE2
    export JINJAMATOR_AAA_THENAMEFORTHELDAPDOMAIN_ALLOWED_GROUP2_MAP=operator,task_taskcollection1/subdir2,task_demotask2,environment_DEMO|site_SITE2
    # this are the default AD properties
    export JINJAMATOR_AAA_THENAMEFORTHELDAPDOMAIN_GROUP_ATTR=memberOf
    export JINJAMATOR_AAA_THENAMEFORTHELDAPDOMAIN_USERNAME_ATTR=samAccountName
    # the jinjamator ldap aaa module recusivly resolve groups, but beware this can result in slow logins. 
    # To limit the impact define at which recursion level jinjamator should stop resolving groups in groups.
    export JINJAMATOR_AAA_THENAMEFORTHELDAPDOMAIN_MAXIMUM_GROUP_RECURSION=1
    jinjamator -t `pipx runpip jinjamator show jinjamator | grep Location | cut -d ' ' -f 2`/jinjamator/tasks/.internal/init_aaa


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