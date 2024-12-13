Quickstart Daemon Mode
=======================


Start jinjamator In Daemon Mode
--------------------------------

To run jinjamator in daemon mode just run it with the -d option. This will start jinjamator with default settings listening on 127.0.0.1 port 5000.

.. code:: shell

    jinjamator -d 


Command Line Options
---------------------

There are many options that can be passed via command line, environment variables or configuration files.
All currently supported options can be viewed by running.


.. code:: shell
    
    someone@somemachine:~$ jinjamator --help

    usage: jinjamator [-h] [-c CONFIGURATION_FILE] [-o OUTPUT_PLUGIN] [-m MAPPING] [-t _TASKDIR] [--best-effort] [-v] [-V]
                    [-g _GLOBAL_DEFAULTS] [-d] [--listen-address _DAEMON_LISTEN_ADDRESS]
                    [--listen-port _DAEMON_LISTEN_PORT] [--no-worker] [--just-worker]
                    [--celery-broker-url _CELERY_BROKER] [--celery-result-backend _CELERY_RESULT_BACKEND]
                    [--celery-result-expires _CELERY_RESULT_EXPIRES] [--max-celery-worker _MAX_CELERY_WORKER]
                    [--celery-beat-database _CELERY_BEAT_DATABASE] [--celery-beat-timezone _CELERY_BEAT_TIMEZONE]
                    [--task-base-dir _GLOBAL_TASKS_BASE_DIRS]
                    [--output-plugin-base-dir _GLOBAL_OUTPUT_PLUGINS_BASE_DIRS]
                    [--content-plugin-base-dir _GLOBAL_CONTENT_PLUGINS_BASE_DIRS]
                    [--environment-base-dir _GLOBAL_ENVIRONMENTS_BASE_DIRS]
                    [--aaa-configuration-base-dir _AAA_CONFIGURATION_BASE_DIRS]
                    [--aaa-database-uri _GLOBAL_AAA_DATABASE_URI] [--secret-key _SECRET-KEY]
                    [--aaa-token-lifetime _AAA_TOKEN_LIFETIME] [--aaa-token-auto-renew_time _AAA_TOKEN_AUTO_RENEW_TIME]
                    [--web-ui-class _WEB_UI_CLASS] [--uploads-folder _UPLOADS_FOLDER] [--enable-task-debugger]
                    [--debugger-port-range _DEBUGGER_PORT_RANGE] [--keep-debug-logs _KEEP_DEBUG_LOGS]
                    [--run-db-maintenance-at _RUN_DB_MAINTENANCE_AT] [--console-pretty-print]

    Copyright 2024 Wilhelm Putz

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    USAGE

    options:
    -h, --help            show this help message and exit
    -c CONFIGURATION_FILE, --configuration-file CONFIGURATION_FILE
                            config file path
    -o OUTPUT_PLUGIN, --output-plugin OUTPUT_PLUGIN
                            selects the plugin which is used for futher data processing after tasklet template has been
                            rendered [default: None] (CLI only)
    -m MAPPING, --mapping MAPPING
                            map data (strings,integer or json) to a variable, e.g. -m 'var_name:asdf' or -m
                            'var_name:{"key":"value"}' (CLI only)
    -t _TASKDIR, --task-dir _TASKDIR
                            path to task directory or tasklet file which should be run (CLI only)
    --best-effort         allow tasklets to fail (CLI only)
    -v, --verbose         set verbosity level [default: ERROR]
    -V, --version         show program's version number and exit
    -g _GLOBAL_DEFAULTS, --global-defaults _GLOBAL_DEFAULTS
                            path to a global defaults.yaml [default: None]
    -d, --daemonize       run in daemon mode
    --listen-address _DAEMON_LISTEN_ADDRESS
                            on which ip should the daemon listen [default: 127.0.0.1] [env var:
                            JINJAMATOR_DAEMON_LISTEN_ADDRESS]
    --listen-port _DAEMON_LISTEN_PORT
                            on which TCP port should the daemon listen [default: 5000] [env var:
                            JINJAMATOR_DAEMON_LISTEN_PORT]
    --no-worker           do not spawn local celery worker [env var: JINJAMATOR_DAEMON_NO_WORKER]
    --just-worker         spawn worker only [env var: JINJAMATOR_DAEMON_JUST_WORKER]
    --celery-broker-url _CELERY_BROKER
                            celery broker URL (required for daemon mode) [default: filesystem://] [env var:
                            JINJAMATOR_DAEMON_CELERY_BROKER_URL]
    --celery-result-backend _CELERY_RESULT_BACKEND
                            celery result backend URL (required for daemon mode) [default:
                            sqlite:////home/putzw/.jinjamator/jinjamator-results.db] [env var:
                            JINJAMATOR_DAEMON_CELERY_RESULT_BACKEND_URL]
    --celery-result-expires _CELERY_RESULT_EXPIRES
                            lifetime of results in the database [default: keep results forever] [env var:
                            JINJAMATOR_DAEMON_CELERY_RESULT_EXPIRES]
    --max-celery-worker _MAX_CELERY_WORKER
                            maximum workers to fork [default: 2] [env var: JINJAMATOR_MAX_CELERY_WORKER]
    --celery-beat-database _CELERY_BEAT_DATABASE
                            celery result beat Database (required for daemon mode) [default:
                            /home/putzw/.jinjamator/jinjamator-beat.db] [env var: JINJAMATOR_DAEMON_CELERY_BEAT_DB_PATH]
    --celery-beat-timezone _CELERY_BEAT_TIMEZONE
                            Timezone celery beat should use [default: UTC] [env var: JINJAMATOR_CELERY_BEAT_TZ]
    --task-base-dir _GLOBAL_TASKS_BASE_DIRS
                            where should jinjamator look for tasks in daemon mode [default:
                            ['/home/putzw/.jinjamator/tasks',
                            '/home/putzw/.local/pipx/venvs/jinjamator/lib/python3.11/site-packages/jinjamator/tasks']]
                            [env var: JINJAMATOR_DAEMON_TASK_BASE_DIRECTORIES]
    --output-plugin-base-dir _GLOBAL_OUTPUT_PLUGINS_BASE_DIRS
                            where should jinjamator look for output plugins [default:
                            ['/home/putzw/.local/pipx/venvs/jinjamator/lib/python3.11/site-
                            packages/jinjamator/plugins/output']] [env var:
                            JINJAMATOR_DAEMON_OUTPUT_PLUGINS_BASE_DIRECTORIES]
    --content-plugin-base-dir _GLOBAL_CONTENT_PLUGINS_BASE_DIRS
                            where should jinjamator look for content plugins [default:
                            ['/home/putzw/.local/pipx/venvs/jinjamator/lib/python3.11/site-
                            packages/jinjamator/plugins/content']] [env var:
                            JINJAMATOR_DAEMON_CONTENT_PLUGINS_BASE_DIRECTORIES]
    --environment-base-dir _GLOBAL_ENVIRONMENTS_BASE_DIRS
                            where should jinjamator look for environments [default:
                            ['/home/putzw/.jinjamator/environments']] [env var:
                            JINJAMATOR_DAEMON_ENVIRONMENTS_BASE_DIRECTORIES]
    --aaa-configuration-base-dir _AAA_CONFIGURATION_BASE_DIRS
                            where should jinjamator look for aaa configuration files [default:
                            ['/home/putzw/.jinjamator/aaa']] [env var: JINJAMATOR_DAEMON_AAA_BASE_DIRECTORIES]
    --aaa-database-uri _GLOBAL_AAA_DATABASE_URI
                            celery result backend URL (required for daemon mode) [default:
                            sqlite:////home/putzw/.jinjamator/aaa/jinjamator-aaa.db] [env var:
                            JINJAMATOR_DAEMON_AAA_DATABASE_URL]
    --secret-key _SECRET-KEY
                            FLASK application secret key, which is used for token generation (required for daemon mode)
                            [default: autogenerated] [env var: JINJAMATOR_DAEMON_SECRET_KEY]
    --aaa-token-lifetime _AAA_TOKEN_LIFETIME
                            API JWT token lifetime [default: 600] [env var: JINJAMATOR_AAA_TOKEN_LIFETIME]
    --aaa-token-auto-renew_time _AAA_TOKEN_AUTO_RENEW_TIME
                            Renew API JWT token automatically if token lifetime is below this. Set to 0 to disable auto
                            renew [default: 300] [env var: JINJAMATOR_AAA_TOKEN_AUTO_RENEW_TIME]
    --web-ui-class _WEB_UI_CLASS
                            classpath to web UI [default: jinjamator.daemon.webui] [env var: JINJAMATOR_WEB_UI_CLASS]
    --uploads-folder _UPLOADS_FOLDER
                            Target Folder for via api uploaded files [default: /tmp/uploads] [env var:
                            JINJAMATOR_UPLOADS_FOLDER]
    --enable-task-debugger
                            Enables webpdb for tasks. CLI Tasks will break on __run__. Daemon tasks can be run with the
                            debug flag [env var: JINJAMATOR_ENABLE_DEBUGGER]
    --debugger-port-range _DEBUGGER_PORT_RANGE
                            If the task debugger is enabled the a port within this port range will be used [env var:
                            JINJAMATOR_DEBUGGER_PORTS]
    --keep-debug-logs _KEEP_DEBUG_LOGS
                            Days to keep the debug logs of each task run. Use <=0 to disable [default: 30] [env var:
                            JINJAMATOR_KEEP_DEBUG_LOGS]
    --run-db-maintenance-at _RUN_DB_MAINTENANCE_AT
                            Specify when to run DB maintenance in crontab syntax (<minute> <hour> <day_of_week>
                            <day_of_month> <month_of_year>) [default: 30 3 * * *] which means daily at 03:30. [env var:
                            JINJAMATOR_RUN_DB_MAINTENANCE_AT]
    --console-pretty-print
                            use pprint instead of print

    Args that start with '--' can also be set in a config file (~/.jinjamator/conf.d/*.yaml or specified via -c). Config
    file syntax allows: key=value, flag=true, stuff=[a,b,c] (for details, see syntax at https://goo.gl/R74nmi). In
    general, command-line values override environment variables which override config file values which override defaults.


The Jinjamator Home Directory
--------------------------------

Jinjamator's default home directory is located at ~/.jinjamator.
This directory contains all data related to the daemon mode, including:

    - Local tasks
    - Logs
    - Environments
    - Log Database
    - AAA Database

For backup purposes, it is sufficient to backup the entire ~/.jinjamator directory.

