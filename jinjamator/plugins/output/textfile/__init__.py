import sys
import os
from jinjamator.tools.output_plugin_base import outputPluginBase
from pprint import pprint
import os
import json
import errno
import tempfile

class textfile(outputPluginBase):
    def addArguments(self):
        self._parent._parser.add_argument(
            "--textfile-file-prefix",
            dest="textfile_file_prefix",
            help="destination file name prefix [default: %(default)s]",
            default="",
        )
        self._parent._parser.add_argument(
            "--textfile-file-suffix",
            dest="textfile_file_suffix",
            help="destination file name suffix [default: %(default)s]",
            default="txt",
        )
        self._parent._parser.add_argument(
            "--textfile-output-directory",
            dest="textfile_output_directory",
            help="destination directory for generated files",
            default="/tmp",
        )

    def connect(self, **kwargs):
        pass

    def process(self, data, **kwargs):
        if self._parent._configuration.get("task_run_mode") == "background":
                    self._parent.configuration["textfile_output_directory"] = os.path.join(
                        self._parent._configuration.get(
                            "jinjamator_user_directory", tempfile.gettempdir()
                        ),
                        "logs",
                        self._parent._configuration.get("jinjamator_job_id"),
                        "files",
                    )

        try:
            os.makedirs(
                self._parent.configuration.get("textfile_output_directory", "./"), exist_ok=True
            )
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
            pass

        generated_filename = "{0}{1}.{2}".format(
            self._parent.configuration.get("textfile_file_prefix", ""),
            os.path.basename(kwargs["template_path"]),
            self._parent.configuration.get("textfile_file_suffix", "txt"),
        )
        generated_dest = os.path.join(
            self._parent.configuration.get("textfile_output_directory", "/tmp"),
            generated_filename,
        )
        dest = self._parent.configuration.get("textfile_output_path", generated_dest)
        if self._parent.configuration.get("textfile_file_suffix") == "json":
            if not isinstance(data,str):
                try:
                    data=json.dumps(data,indent=2, sort_keys=True)
                except ValueError:
                    data=json.dumps(data,indent=2, sort_keys=False)

        with open(dest, "w") as fh:
            fh.write(data)
        self._log.info("sucessfully written file: {0}".format(dest))
