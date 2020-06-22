#!/usr/bin/env python3
# Copyright 2019 Wilhelm Putz

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
swiss army knife automation tool
"""

import sys
import os
import logging
from glob import glob
import tempfile
import random
import string


from configargparse import ArgumentParser
from configargparse import RawDescriptionHelpFormatter


from jinjamator.task.configuration import TaskConfiguration
from jinjamator.plugin_loader.output import load_output_plugin
from jinjamator.tools.version import version, updated


__version__ = version
__updated__ = updated
__date__ = "22.07.2019"
__author__ = "Wilhelm Putz"


class Program(object):
    def __init__(self, argv=None):
        self._children = []
        if argv is None:
            argv = sys.argv
        else:
            sys.argv.extend(argv)
        self._program_name = os.path.basename(sys.argv[0])
        self._program_version = "v%s" % __version__
        self._program_build_date = str(__updated__)
        self._program_shortdesc = __import__("__main__").__doc__.split("\n")[1]
        self._program_date = str(__date__)
        self._program_author = __author__
        self._configuration = {}
        self.configuration = {}
        self._configuration["jinjamator_user_directory"] = os.path.sep.join(
            [os.path.expanduser("~"), ".jinjamator"]
        )
        self._configuration["jinjamator_base_directory"] = os.path.dirname(
            os.path.realpath(__file__)
        )
        self._output_plugin = None

    def addArguments(self):
        self._parser.add_argument(
            "-h",
            "--help",
            dest="help",
            action="count",
            help="show this help message and exit",
        )
        self._parser.add(
            "-c",
            "--configuration-file",
            required=False,
            is_config_file=True,
            help="config file path",
        )

        self._parser.add_argument(
            "-o",
            "--output-plugin",
            dest="output_plugin",
            help="selects the plugin which is used for futher data processing after tasklet template has been rendered [default: %(default)s] (CLI only)",
            default="console",
        )
        self._parser.add_argument(
            "-m",
            "--mapping",
            dest="mapping",
            help="map data (strings,integer or json) to a variable, e.g. -m 'var_name:asdf' or -m 'var_name:{\"key\":\"value\"}' (CLI only)",
            action="append",
        )
        self._parser.add_argument(
            "-t",
            "--task-dir",
            dest="_taskdir",
            help="path to task directory or tasklet file which should be run (CLI only)",
        )
        self._parser.add_argument(
            "--best-effort",
            dest="best_effort",
            default=False,
            action="store_true",
            help="allow tasklets to fail (CLI only)",
        )

        self._parser.add_argument(
            "-v",
            "--verbose",
            dest="_verbose",
            action="count",
            help="set verbosity level [default: ERROR]",
        )
        self._parser.add_argument(
            "-V", "--version", action="version", version=self._program_version_message
        )
        self._parser.add_argument(
            "-g",
            "--global-defaults",
            dest="_global_defaults",
            default=None,
            help="path to a global defaults.yaml [default: %(default)s]",
        )

        self._parser.add_argument(
            "-d",
            "--daemonize",
            dest="_daemonize",
            default=False,
            action="store_true",
            help="run in daemon mode",
        )
        self._parser.add_argument(
            "--listen-address",
            dest="_daemon_listen_address",
            default="127.0.0.1",
            help="on which ip should the daemon listen [default: %(default)s]",
            env_var="JINJAMATOR_DAEMON_LISTEN_ADDRESS",
        )
        self._parser.add_argument(
            "--listen-port",
            dest="_daemon_listen_port",
            default="5000",
            help="on which TCP port should the daemon listen [default: %(default)s]",
            env_var="JINJAMATOR_DAEMON_LISTEN_PORT",
        )
        self._parser.add_argument(
            "--no-worker",
            dest="_no_worker",
            default=False,
            action="store_true",
            help="do not spawn local celery worker",
            env_var="JINJAMATOR_DAEMON_NO_WORKER",
        )
        self._parser.add_argument(
            "--just-worker",
            dest="_just_worker",
            default=False,
            action="store_true",
            help="spawn worker only",
            env_var="JINJAMATOR_DAEMON_JUST_WORKER",
        )
        self._parser.add_argument(
            "--celery-broker-url",
            dest="_celery_broker",
            # default="amqp://jinjamator:jinjamator@localhost:5672/jinjamator",
            default=f"filesystem://",
            help="celery broker URL (required for daemon mode)  [default: %(default)s]",
            env_var="JINJAMATOR_DAEMON_CELERY_BROKER_URL",
        )
        self._parser.add_argument(
            "--celery-result-backend",
            dest="_celery_result_backend",
            default=f'sqlite:///{self._configuration.get("jinjamator_user_directory",tempfile.gettempdir())}/jinjamator-results.db',
            help="celery result backend URL (required for daemon mode)  [default: %(default)s]",
            env_var="JINJAMATOR_DAEMON_CELERY_RESULT_BACKEND_URL",
        )
        self._parser.add_argument(
            "--celery-heartbeat-database",
            dest="_celery_beat_database",
            default=f'{self._configuration.get("jinjamator_user_directory", tempfile.gettempdir())}/jinjamator-beat.db',
            help="celery result beat Database (required for daemon mode)  [default: %(default)s]",
            env_var="JINJAMATOR_DAEMON_CELERY_BEAT_DB_PATH",
        )
        self._parser.add_argument(
            "--task-base-dir",
            dest="_global_tasks_base_dirs",
            default=[
                os.path.sep.join(
                    [self._configuration["jinjamator_user_directory"], "tasks"]
                ),
                os.path.sep.join(
                    [self._configuration["jinjamator_base_directory"], "tasks"]
                ),
            ],
            action="append",
            help="where should jinjamator look for tasks in daemon mode [default: %(default)s]",
            env_var="JINJAMATOR_DAEMON_TASK_BASE_DIRECTORIES",
        )

        self._parser.add_argument(
            "--output-plugin-base-dir",
            dest="_global_output_plugins_base_dirs",
            default=[
                os.path.sep.join(
                    [
                        self._configuration["jinjamator_base_directory"],
                        "plugins",
                        "output",
                    ]
                )
            ],
            action="append",
            help="where should jinjamator look for output plugins  [default: %(default)s]",
            env_var="JINJAMATOR_DAEMON_OUTPUT_PLUGINS_BASE_DIRECTORIES",
        )

        self._parser.add_argument(
            "--content-plugin-base-dir",
            dest="_global_content_plugins_base_dirs",
            default=[
                os.path.sep.join(
                    [
                        self._configuration["jinjamator_base_directory"],
                        "plugins",
                        "content",
                    ]
                )
            ],
            action="append",
            help="where should jinjamator look for content plugins  [default: %(default)s]",
            env_var="JINJAMATOR_DAEMON_CONTENT_PLUGINS_BASE_DIRECTORIES",
        )

        self._parser.add_argument(
            "--environment-base-dir",
            dest="_global_environments_base_dirs",
            default=[
                os.path.sep.join(
                    [self._configuration["jinjamator_user_directory"], "environments"]
                )
            ],
            action="append",
            help="where should jinjamator look for environments [default: %(default)s]",
            env_var="JINJAMATOR_DAEMON_ENVIRONMENTS_BASE_DIRECTORIES",
        )

        self._parser.add_argument(
            "--aaa-configuration-base-dir",
            dest="_aaa_configuration_base_dirs",
            default=[
                os.path.sep.join(
                    [self._configuration["jinjamator_user_directory"], "aaa"]
                )
            ],
            action="append",
            help="where should jinjamator look for aaa configuration files [default: %(default)s]",
            env_var="JINJAMATOR_DAEMON_AAA_BASE_DIRECTORIES",
        )

        self._parser.add_argument(
            "--aaa-database-uri",
            dest="_global_aaa_database_uri",
            default=f'sqlite:///{self._configuration.get("jinjamator_user_directory",tempfile.gettempdir())}/aaa/jinjamator-aaa.db',
            help="celery result backend URL (required for daemon mode)  [default: %(default)s]",
            env_var="JINJAMATOR_DAEMON_AAA_DATABASE_URL",
        )

        generated_secret = "".join(
            random.SystemRandom().choice(string.ascii_letters + string.digits)
            for _ in range(128)
        )
        self._parser.add_argument(
            "--secret-key",
            dest="_secret-key",
            default=generated_secret,
            help="FLASK application secret key, which is used for token generation (required for daemon mode)  [default: autogenerated]",
            env_var="JINJAMATOR_DAEMON_SECRET_KEY",
        )

        self._parser.add_argument(
            "--aaa-token-lifetime",
            dest="_aaa_token_lifetime",
            default=600,
            help="API JWT token lifetime [default: %(default)s]",
            env_var="JINJAMATOR_AAA_TOKEN_LIFETIME",
        )
        self._parser.add_argument(
            "--aaa-token-auto-renew_time",
            dest="_aaa_token_auto_renew_time",
            default=300,
            help="Renew API JWT token automatically if token lifetime is below this. Set to 0 to disable auto renew [default: %(default)s]",
            env_var="JINJAMATOR_AAA_TOKEN_AUTO_RENEW_TIME",
        )

    def setupLogging(self):
        global logging
        logging.addLevelName(90, "TASKLET_RESULT")

        def tasklet_result(self, message, *args, **kws):
            # Yes, logger takes its '*args' as 'args'.
            self._log(90, message, args, **kws)

        logging.Logger.tasklet_result = tasklet_result

        msg_format = "%(asctime)s - %(process)d - %(threadName)s - [%(pathname)s:%(lineno)s] - %(funcName)s - %(levelname)s - %(message)s"
        stdout = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(msg_format)
        stdout.setFormatter(formatter)
        self._log = logging.getLogger()
        self._log.addHandler(stdout)

    def setup(self):
        self.setupLogging()

        self._program_version_message = "%%(prog)s %s (%s)" % (
            self._program_version,
            self._program_build_date,
        )
        self._program_license = f"""{self._program_shortdesc}

  Copyright 2019 Wilhelm Putz
  
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
"""
        try:
            # Setup argument parser
            self._parser = ArgumentParser(
                description=self._program_license,
                formatter_class=RawDescriptionHelpFormatter,
                add_help=False,
                default_config_files=["~/.jinjamator/conf.d/*.yaml"],
            )
            self.addArguments()

            # Process default arguments
            self._args, unknown = self._parser.parse_known_args()

            for arg in vars(self._args):
                if arg.startswith("_"):
                    self._configuration[arg[1:]] = getattr(self._args, arg)
                else:
                    self.configuration[arg] = getattr(self._args, arg)

            load_output_plugin(
                self,
                self.configuration["output_plugin"],
                self._configuration["global_output_plugins_base_dirs"],
            )
            if self._output_plugin:
                self._output_plugin.addArguments()
            self._args, unknown = self._parser.parse_known_args()

            if unknown:
                self._log.warn("unkown arguments found: {0}".format(unknown))

            if self._args.help:
                print(self._parser.format_help())
                sys.exit(0)

            if not self._configuration.get("taskdir") and not self._configuration.get(
                "daemonize"
            ):
                print(self._parser.format_help())
                sys.exit(1)

            verbose = self._configuration.get("verbose") or 0

            if verbose > 0:
                self._log.setLevel(logging.ERROR)
            if verbose > 1:
                self._log.setLevel(logging.WARN)
            if verbose > 2:
                self._log.setLevel(logging.INFO)
            if verbose > 3:
                self._log.setLevel(logging.DEBUG)
            try:
                self._args.config
                self.readConfig(self._args.config)
            except AttributeError:
                pass

            for arg in vars(self._args):
                if arg.startswith("_"):
                    self._configuration[arg[1:]] = getattr(self._args, arg)
                else:
                    self.configuration[arg] = getattr(self._args, arg)

            if self._configuration["taskdir"]:
                self._configuration["taskdir"] = os.path.abspath(
                    self._configuration["taskdir"]
                )

            for index, global_tasks_base_dir in enumerate(
                self._configuration["global_tasks_base_dirs"]
            ):
                self._configuration["global_tasks_base_dirs"][index] = os.path.abspath(
                    global_tasks_base_dir
                )

        except Exception as e:
            raise (e)

    def run(self):
        self._log.debug("called run")
        try:
            self.main()
        except KeyboardInterrupt:
            sys.exit(0)

    def main(self):
        for d in ["environments", "logs", "tasks", "uploads", "aaa", "conf.d"]:
            os.makedirs(
                os.path.sep.join([self._configuration["jinjamator_user_directory"], d]),
                exist_ok=True,
            )

        if self._configuration["daemonize"]:
            from jinjamator.daemon import run as app_run

            app_run(self._configuration)

        else:
            # legacy cli task
            from jinjamator.task import JinjamatorTask

            task = JinjamatorTask("interactive")
            if self._configuration["global_defaults"]:
                task.configuration.merge_yaml(self._configuration["global_defaults"])

            task.configuration.merge_dict(self.configuration)
            task._configuration.merge_dict(self._configuration)

            task.load_output_plugin(
                self.configuration["output_plugin"],
                self._configuration["global_output_plugins_base_dirs"],
            )

            try:
                task.load(self._configuration["taskdir"])
            except ValueError:
                if os.path.isdir(self._configuration["taskdir"]):
                    self._log.error(
                        f'No Tasklets found in {self._configuration["taskdir"]} -> exiting'
                    )
                else:
                    self._log.error(
                        f'Task directory {self._configuration["taskdir"]} not found -> exiting'
                    )
            task.run()


if __name__ == "__main__":
    prog = Program()
    prog._program_version = __version__
    prog._program_date = __date__
    prog._program_build_date = __updated__
    prog._program_author = __author__
    prog.setup()
    prog.run()
