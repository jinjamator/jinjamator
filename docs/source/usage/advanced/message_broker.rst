Jinjamator uses `Celery <http://www.celeryproject.org/>`_ as a distributed task queue. 
For optimal operation Celery_ needs `RabbitMQ <https://www.rabbitmq.com/>`_ as a message broker. 

Install RabbitMQ_.

.. code:: shell

    sudo apt install rabbitmq

(optional) Enable RabbitMQ_ autostart.

.. code:: shell

    sudo systemctl enable rabbitmq-server

Start RabbitMQ_ service.

.. code:: shell

    sudo systemctl start rabbitmq-server

Create a RabbitMQ_ virtual host.

.. code:: shell

    sudo rabbitmqctl add_vhost jinjamator


Create a RabbitMQ_ user and set permissions.

.. code:: shell

    sudo rabbitmqctl add_user jinjamator superSecretPassword
    sudo rabbitmqctl set_permissions -p jinjamator jinjamator ".*" ".*" ".*"


