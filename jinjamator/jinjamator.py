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


from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import sys
import os
from jinjamator.task.configuration import TaskConfiguration
import logging
from glob import glob
import tempfile
from jinjamator.plugin_loader.output import load_output_plugin

__version__ = "0.4.2"
__updated__ = "11.05.2020"
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
        self._cfg = {}
        self._cfg["jinjamator_user_directory"] = os.path.sep.join(
            [os.path.expanduser("~"), ".jinjamator"]
        )
        self._cfg["jinjamator_base_directory"] = os.path.dirname(
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
        self._parser.add_argument(
            "-o",
            "--output-plugin",
            dest="output_plugin",
            help="selects the plugin which is used for futher data processing after tasklrt template has been rendered [default: %(default)s]",
            default="console",
        )
        self._parser.add_argument(
            "-m",
            "--mapping",
            dest="mapping",
            help="map data (strings,integer or json) to a variable, e.g. -m 'var_name:asdf' or -m 'var_name:{\"key\":\"value\"}' ",
            action="append",
        )
        self._parser.add_argument(
            "-t",
            "--task-dir",
            dest="taskdir",
            help="task directory with task descriptions",
        )
        self._parser.add_argument(
            "-v",
            "--verbose",
            dest="verbose",
            action="count",
            help="set verbosity level [default: ERROR]",
        )
        self._parser.add_argument(
            "-V", "--version", action="version", version=self._program_version_message
        )
        self._parser.add_argument(
            "-g",
            "--global-defaults",
            dest="global_defaults",
            default=None,
            help="path to a global defaults.yaml [default: %(default)s]",
        )
        self._parser.add_argument(
            "--best-effort",
            dest="best_effort",
            default=False,
            action="store_true",
            help="allow task items to fail",
        )
        self._parser.add_argument(
            "-d",
            "--daemonize",
            dest="daemonize",
            default=False,
            action="store_true",
            help="run in daemon mode",
        )
        self._parser.add_argument(
            "--no-worker",
            dest="no_worker",
            default=False,
            action="store_true",
            help="do not spawn local celery worker",
        )
        self._parser.add_argument(
            "--just-worker",
            dest="just_worker",
            default=False,
            action="store_true",
            help="spawn worker only",
        )
        self._parser.add_argument(
            "--celery-broker-url",
            dest="celery_broker",
            default="amqp://jinjamator:jinjamator@localhost:5672/jinjamator",
            help="celery broker URL (required for daemon mode)  [default: %(default)s]",
        )
        self._parser.add_argument(
            "--celery-result-backend",
            dest="celery_result_backend",
            default=f'sqlite:///{self._cfg.get("jinjamator_user_directory",tempfile.gettempdir())}/jinjamator-results.db',
            help="celery result backend URL (required for daemon mode)  [default: %(default)s]",
        )
        self._parser.add_argument(
            "--celery-heartbeat-database",
            dest="celery_beat_database",
            default=f'{self._cfg.get("jinjamator_user_directory", tempfile.gettempdir())}/jinjamator-beat.db',
            help="celery result beat Database (required for daemon mode)  [default: %(default)s]",
        )
        self._parser.add_argument(
            "--task-base-dir",
            dest="global_tasks_base_dirs",
            default=[
                os.path.sep.join([self._cfg["jinjamator_user_directory"], "tasks"]),
                os.path.sep.join([self._cfg["jinjamator_base_directory"], "tasks"]),
            ],
            action="append",
            help="where should jinjamator look for tasks  [default: %(default)s]",
        )

        self._parser.add_argument(
            "--output-plugin-base-dir",
            dest="global_output_plugins_base_dirs",
            default=[
                os.path.sep.join(
                    [self._cfg["jinjamator_base_directory"], "plugins", "output"]
                )
            ],
            action="append",
            help="where should jinjamator look for output plugins  [default: %(default)s]",
        )

        self._parser.add_argument(
            "--content-plugin-base-dir",
            dest="global_content_plugins_base_dirs",
            default=[
                os.path.sep.join(
                    [self._cfg["jinjamator_base_directory"], "plugins", "content"]
                )
            ],
            action="append",
            help="where should jinjamator look for output plugins  [default: %(default)s]",
        )

        self._parser.add_argument(
            "--environment-base-dir",
            dest="global_environments_base_dirs",
            default=[
                os.path.sep.join(
                    [self._cfg["jinjamator_user_directory"], "environments"]
                )
            ],
            action="append",
            help="where should jinjamator look for environments [default: %(default)s]",
        )

    def setupLogging(self):
        global logging
        logging.addLevelName(90, "TASKLET_RESULT")

        def tasklet_result(self, message, *args, **kws):
            # Yes, logger takes its '*args' as 'args'.
            self._log(90, message, args, **kws)

        logging.Logger.tasklet_result = tasklet_result

        msg_format = "%(asctime)s - %(process)d - %(threadName)s - %(funcName)s - %(levelname)s - %(message)s"
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
            )
            self.addArguments()

            # Process default arguments
            self._args, unknown = self._parser.parse_known_args()

            for arg in vars(self._args):
                self._cfg[arg] = getattr(self._args, arg)

            load_output_plugin(
                self,
                self._cfg["output_plugin"],
                self._cfg["global_output_plugins_base_dirs"],
            )
            if self._output_plugin:
                self._output_plugin.addArguments()
            self._args, unknown = self._parser.parse_known_args()

            if unknown:
                self._log.warn("unkown arguments found: {0}".format(unknown))

            if self._args.help:
                print(self._parser.format_help())
                sys.exit(0)

            if not self._args.taskdir and not self._args.daemonize:
                print(self._parser.format_help())
                sys.exit(1)

            verbose = self._args.verbose or 0

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
                self._cfg[arg] = getattr(self._args, arg)

            if self._cfg["taskdir"]:
                self._cfg["taskdir"] = os.path.abspath(self._cfg["taskdir"])

            for index, global_tasks_base_dir in enumerate(
                self._cfg["global_tasks_base_dirs"]
            ):
                self._cfg["global_tasks_base_dirs"][index] = os.path.abspath(
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
        for d in ["environments", "logs", "tasks"]:
            os.makedirs(
                os.path.sep.join([self._cfg["jinjamator_user_directory"], d]),
                exist_ok=True,
            )

        if self._cfg["daemonize"]:
            if os.path.isfile("/proc/version"):
                # Attempt to screen out WSL users, since it is currently (01.04.2020) known to be broken.
                try:
                    with open("/proc/version", "r") as o:
                        txt = o.read()
                        if "MICROSOFT" in txt.upper():
                            self._log.error(
                                "Running jinjamator daemon mode in WSL currently is not supported, and will corrupt sqlite databases. See https://github.com/microsoft/WSL/issues/2395"
                            )
                            sys.exit(1)
                except Exception as e:
                    self._log.error(e)
            from jinjamator.daemon import app

            app.config["CELERY_BROKER_URL"] = self._cfg["celery_broker"]
            app.config["CELERY_RESULT_BACKEND"] = self._cfg["celery_result_backend"]
            app.config["SQLALCHEMY_DATABASE_URI"] = self._cfg["celery_result_backend"]
            app.config["JINJAMATOR_BASE_DIRECTORY"] = self._cfg[
                "jinjamator_base_directory"
            ]
            app.config["UPLOAD_FOLDER"] = os.path.join(
                self._cfg["jinjamator_base_directory"], "var/uploads"
            )

            if len(self._cfg["global_environments_base_dirs"]) == 0:
                self._cfg["global_environments_base_dirs"] = [
                    "{0}{1}environments".format(
                        self._cfg["jinjamator_base_directory"], os.path.sep
                    )
                ]
            app.config["JINJAMATOR_GLOBAL_DEFAULTS"] = self._cfg["global_defaults"]
            app.config["JINJAMATOR_TASKS_BASE_DIRECTORIES"] = self._cfg[
                "global_tasks_base_dirs"
            ]
            app.config["JINJAMATOR_ENVIRONMENTS_BASE_DIRECTORIES"] = self._cfg[
                "global_environments_base_dirs"
            ]
            app.config["JINJAMATOR_OUTPUT_PLUGINS_BASE_DIRS"] = self._cfg[
                "global_output_plugins_base_dirs"
            ]
            app.config["JINJAMATOR_CONTENT_PLUGINS_BASE_DIRS"] = self._cfg[
                "global_content_plugins_base_dirs"
            ]

            from jinjamator.daemon import views

            if not self._cfg["no_worker"]:
                self._cfg["no_worker"] = True

                if "WERKZEUG_RUN_MAIN" not in os.environ.keys():
                    pid = os.fork()
                    if pid == 0:
                        from celery import Celery

                        queue = Celery("jinjamator", broker=self._cfg["celery_broker"])
                        queue.start(
                            argv=[
                                "celery",
                                "worker",
                                "-c",
                                "8",
                                "--max-tasks-per-child",
                                "1",
                                "-b",
                                self._cfg["celery_broker"],
                                "-B",
                                "-s",
                                self._cfg["celery_beat_database"],
                            ]
                        )
                        sys.exit(0)
                    else:
                        if not self._cfg["just_worker"]:
                            app.run(debug=True, host="0.0.0.0")
                        os.waitpid(pid, 0)
                else:

                    app.run(debug=True, host="0.0.0.0")
            else:
                app.run(debug=True, host="0.0.0.0")

        else:
            # add legacy task execution code here
            from jinjamator.task import JinjamatorTask

            task = JinjamatorTask("interactive")
            if self._cfg["global_defaults"]:
                task.configuration.merge_yaml(self._cfg["global_defaults"])
            task.configuration.merge_dict(self._cfg)

            task.load_output_plugin(
                self._cfg["output_plugin"], self._cfg["global_output_plugins_base_dirs"]
            )

            try:
                task.load(self._cfg["taskdir"])
            except ValueError:
                if os.path.isdir(self._cfg["taskdir"]):
                    self._log.error(
                        f'No Tasklets found in {self._cfg["taskdir"]} -> exiting'
                    )
                else:
                    self._log.error(
                        f'Task directory {self._cfg["taskdir"]} not found -> exiting'
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
