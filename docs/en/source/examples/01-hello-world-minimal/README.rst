
Hello World
-------------
This example just asks yout input the value for a variable named var_name and returns this value as string 'Hello <data you typed in>'
Just to show you that python and jinja2 are handled totally equal, this example is written in both languages.

CLI
*****

to run the python example

.. code-block:: bash

    jinjamator -t <path to examples>/01-hello-world-minimal/python

to run the jinja2 example execute

.. code-block:: bash

    jinjamator -t <path to examples>/01-hello-world-minimal/jinja2

Web
*****
To start the daemon setup RabbitMQ as described in the installation section and run jinjamator with following command.

.. code-block:: bash

    jinjamator --task-base-dir <path to examples> --celery-broker-url amqp://jinjamator:<password chosen at setup>@localhost:5672/jinjamator

